from flask import Flask, render_template, jsonify, request, current_app, redirect, url_for
from context import Context
import json
from openai import OpenAI
import openai
import os
from systemprompts import SystemPrompts
import sys
import datetime
import threading
import queue
import atexit
from videoGen import generate_video
from mappings import *
import random
import html

app = Flask(__name__, template_folder='static/templates')
global context 
MAX_WORKERS = 6
# Create multiple queues for video generation tasks
video_queues = [queue.Queue() for _ in range(MAX_WORKERS)]
video_status = {}  # Dictionary to track video generation status
current_queue = 0  # For round-robin distribution

# Add a lock for the job counter
job_counter_lock = threading.Lock()
job_counter = 0

# Add a lock for the current_queue counter
queue_lock = threading.Lock()

# Add a lock for the video_status dictionary
video_status_lock = threading.Lock()

def video_worker(worker_id):
    global job_counter
    while True:
        try:
            task = video_queues[worker_id].get(timeout=360)
        except queue.Empty:
            with open("video_queue.log", "a") as logfile:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                thread_id = threading.current_thread().ident
                logfile.write(f"[{current_time}] Worker {worker_id} (Thread ID: {thread_id}) timed out, shutting down\n")
            break
            
        if task is None:
            break
            
        user_id, response_data = task
        try:
            with open("video_queue.log", "a") as logfile:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                thread_id = threading.current_thread().ident
                logfile.write(f"[{current_time}] Worker {worker_id} (Thread ID: {thread_id}) processing video for response: {str(response_data)[:200]}...\n")
                
                # Use lock when accessing job_counter
                with job_counter_lock:
                    job_id = job_counter
                    job_counter += 1
                    
                generate_video(response_data, job_id)
            
            with video_status_lock:
                video_status[user_id] = "completed"
            
        except Exception as e:
            with video_status_lock:
                video_status[user_id] = "failed"
            with open("video_queue.log", "a") as logfile:
                thread_id = threading.current_thread().ident
                logfile.write(f"[{current_time}] Worker {worker_id} (Thread ID: {thread_id}) error processing video: {str(e)}\n")
        
        finally:
            video_queues[worker_id].task_done()
            with open("video_queue.log", "a") as logfile:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                thread_id = threading.current_thread().ident
                logfile.write(f"[{current_time}] Worker {worker_id} (Thread ID: {thread_id}) completed task\n")

def add_to_queue(user_id, response_data):
    global current_queue
    video_queues[current_queue].put((user_id, response_data))
    with open("video_queue.log", "a") as logfile:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logfile.write(f"[{current_time}] Added task to queue {current_queue}\n")
    current_queue = (current_queue + 1) % MAX_WORKERS

# Create thread pool
thread_pool = []
for i in range(MAX_WORKERS):
    worker = threading.Thread(target=video_worker, args=(i,), daemon=True)
    thread_pool.append(worker)
    worker.start()
    with open("video_queue.log", "a") as logfile:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logfile.write(f"[{current_time}] Started worker {i}\n")

@app.template_filter('from_json')
def from_json(value):
    return json.loads(value)

def dict_to_string(dict):
    return json.dumps(dict)

def first_prompt(context):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    chat_prompt = {
        "role": "user",
        "content": dict_to_string({
            "current_context": context.get_context()
        })
    }
    response = client.chat.completions.create(
        model=SystemPrompts.MODEL,
        messages=[SystemPrompts.MODEL_DEFINITION_FIRST, chat_prompt]
    )
    return response

def prompt_gpt(user_input, context):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    chat_prompt = {
        "role": "user",
        "content": dict_to_string({
            "user_input": user_input,
            "current_context": context.get_context()
        })
    }
    response = client.chat.completions.create(
        model=SystemPrompts.MODEL,
        messages=[SystemPrompts.MODEL_DEFINITION_RECURSE, chat_prompt]
    )
    return response

@app.route('/previewgamerun')
def previewGameRun():
    dummy_response = {
        "story_output": "As you make your final decision, darkness closes in. Your journey ends here, brave adventurer.",
        "context": {
            "player": {
                "_status": "dead",
                "_location": "forest",
                "_alive": "dead"
            },
            "npcs": [],
            "major_story_events": ["Player died in the forest"],
            "narrative_state": "resolution"
        }
    }
    context = Context(json.load(open("resources/fantasy.json")))    
    return render_template('gameRun.html', context = context.get_context(), response = dict_to_string(dummy_response))

@app.route('/gameEnd')
def endGame():
    return render_template('gameEnd.html')

@app.route('/textScene', methods=['GET', 'POST'])
def textScene():
    # Get index from number of text files
    num = len([name for name in os.listdir('static/video_text') if name.endswith('.txt')])
    index = request.form.get('index', 0, type=int)
    if index == num:
        return render_template('gameEnd.html')
    with open(f"static/video_text/Scene{index}.txt", "r") as f:
        fn = f.read()
        fn = fn.split("CONTEXT:")[0]
        
        return render_template('textScene.html', text=fn, index=index)
    

@app.route('/gameVideo', methods=['GET', 'POST'])
def game_video():
    index = request.form.get('index', 0, type=int)
    path = f"static/videos/Scene{index}.mp4"
    index += 1
    return render_template('gameVideo.html', path=path, index=index)
    

@app.route('/gameRun', methods=['GET', 'POST'])
def runGame():
    if request.method == 'POST':
        if 'first_init' in request.form:
            initial_theme = request.form['initial_theme']
            match initial_theme:
                case "fantasy":
                    init_dict = {}
                    init_dict["available_npcs"] = list(FantasyNPCMap.MAP.keys())
                    init_dict["available_locations"] = list(FantasyLocationMap.MAP.keys())
                    init_dict["initial_prompt"] = f"Fantasy adventure starting in {random.choice(init_dict['available_locations'])}, conflict, "
                    with open("mode.txt", "w") as f:
                        f.write("fantasy")
                case "space":
                    init_dict = {}
                    init_dict["available_npcs"] = list(SpaceNPCMap.MAP.keys())
                    init_dict["available_locations"] = list(SpaceLocationMap.MAP.keys())
                    init_dict["initial_prompt"] = f"Space adventure starting in {random.choice(init_dict['available_locations'])}, conflict, "
                    with open("mode.txt", "w") as f:
                        f.write("space")
            context = Context(init_dict)
            response = first_prompt(context)
            context.update_context(response)
            context.update_npc_context(response)
            
            # Queue video generation for initial response
            message_content = json.loads(response.choices[0].message.content)
            story_output = message_content["story_output"]
            ctxt = message_content["context"]
            past_events = ctxt["major_story_events"]
            past_events_string = ", ".join(past_events)
            input_string = story_output + "CONTEXT: " +past_events_string

            add_to_queue("init", input_string)
            with open("video_queue.log", "a") as logfile:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logfile.write(f"[{current_time}] Queued initial video generation\n")
            
            with open("mode.txt", "r") as f:
                mode = f.read()
            if mode == "fantasy":
                npc_map = FantasyNPCMap.MAP
                location_map = FantasyLocationMap.MAP
            elif mode == "space":
                npc_map = SpaceNPCMap.MAP
                location_map = SpaceLocationMap.MAP

            res_context = json.loads(response.choices[0].message.content)["context"]
            location_img = location_map[res_context["player"]["_location"]]
            npc_description = ""
            
            if res_context['npc_in_scene'] != "":
                npc_img = npc_map[res_context['npc_in_scene']]
                for npc_dict in res_context['npcs']:
                    npc_description = npc_dict['_description'] if npc_dict['_class'] == res_context['npc_in_scene'] else ""
                    hasNPC = True
                    break
                hasNPC = True
            else:
                npc_img = ""
                hasNPC = False

            return render_template('gameRun.html',
                                    context=context.get_context(),
                                    response=response.choices[0].message.content,
                                    location_img=location_img,
                                    npc_img=npc_img,
                                    hasNPC=hasNPC,
                                    npc_description=npc_description)
        
        elif 'game_loop' in request.form:
            context = Context(json.loads(request.form['context_dict']))
            user_input = request.form['player_input']
            response = prompt_gpt(user_input, context)
            context.update_context(response)
            context.update_npc_context(response)
            
            # Queue video generation for each response
            message_content = json.loads(response.choices[0].message.content)
            story_output = message_content["story_output"]
            ctxt = message_content["context"]
            past_events = ctxt["major_story_events"]
            past_events_string = ", ".join(past_events)
            input_string = story_output + "CONTEXT: " +past_events_string
            
            add_to_queue("game_loop", input_string)
            with open("video_queue.log", "a") as logfile:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logfile.write(f"[{current_time}] Queued game loop video generation\n")
            with open("mode.txt", "r") as f:
                mode = f.read()
            if mode == "fantasy":
                npc_map = FantasyNPCMap.MAP
                location_map = FantasyLocationMap.MAP
            elif mode == "space":
                npc_map = SpaceNPCMap.MAP
                location_map = SpaceLocationMap.MAP

            res_context = json.loads(response.choices[0].message.content)["context"]
            location_img = location_map[res_context["player"]["_location"]]
            npc_description = ""
            
            if res_context['npc_in_scene'] != "":
                npc_img = npc_map[res_context['npc_in_scene']]
                for npc_dict in res_context['npcs']:
                    npc_description = npc_dict['_description'] if npc_dict['_class'] == res_context['npc_in_scene'] else ""
                    hasNPC = True
                    break
                hasNPC = True
            else:
                npc_description = ""
                npc_img = ""
                hasNPC = False
            return render_template('gameRun.html',
                                    context=context.get_context(),
                                    response=response.choices[0].message.content,
                                    location_img=location_img,
                                    npc_img=npc_img,
                                    hasNPC=hasNPC,
                                    npc_description=npc_description)

    return render_template('gameRun.html', context='first_init' in request.form)

@app.route('/gameStart')
def startGame():
    return render_template('gameStart.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/howToPlay')
def how_to_play():
    return render_template('howToPlay.html')

@app.route('/loading')
def loading():
    if all(os.path.exists(f"static/video_text/Scene{i}.txt") == os.path.exists(f"static/videos/Scene{i}.mp4") for i in range(10)):
        text_files = [open(f"static/video_text/Scene{i}.txt").read().split("CONTEXT:")[0] for i in range(10) if os.path.exists(f"static/video_text/Scene{i}.txt")]
        video_paths = [f"static/videos/Scene{i}.mp4" for i in range(10) if os.path.exists(f"static/videos/Scene{i}.mp4")]
        return redirect(url_for('textScene', index=0, _method='GET'))
    else:
        return render_template('loading.html')

# Cleanup function to stop workers gracefully
def cleanup_workers():
    # Signal all workers to stop
    for _ in range(MAX_WORKERS):
        video_queues[_].put(None)
    
    # Wait for all workers to finish
    for worker in thread_pool:
        worker.join()
    
    with open("video_queue.log", "a") as logfile:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logfile.write(f"[{current_time}] All workers shut down\n")

# Register cleanup function to run on application shutdown
atexit.register(cleanup_workers)

if __name__ == '__main__':
    app.run(debug=True)