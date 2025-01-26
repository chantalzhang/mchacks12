from flask import Flask, render_template, jsonify, request, current_app
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

app = Flask(__name__, template_folder='static/templates')
global context 

# Create a queue for video generation tasks
video_queue = queue.Queue()
video_status = {}  # Dictionary to track video generation status
MAX_WORKERS = 5  # Maximum number of concurrent threads

def video_worker(worker_id):
    while True:
        try:
            task = video_queue.get(timeout=60)  # Wait up to 60 seconds for new tasks
        except queue.Empty:
            # If no tasks received in 60 seconds, exit thread
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
                generate_video(response_data, worker_id)
            
            video_status[user_id] = "completed"
            
        except Exception as e:
            video_status[user_id] = "failed"
            with open("video_queue.log", "a") as logfile:
                thread_id = threading.current_thread().ident
                logfile.write(f"[{current_time}] Worker {worker_id} (Thread ID: {thread_id}) error processing video: {str(e)}\n")
        
        finally:
            video_queue.task_done()
            with open("video_queue.log", "a") as logfile:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                thread_id = threading.current_thread().ident
                logfile.write(f"[{current_time}] Worker {worker_id} (Thread ID: {thread_id}) completed task\n")

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

@app.route('/textScene')
def textScene():
    return render_template('textScene.html')

@app.route('/gameVideo')
def gameVideo():
    return render_template('gameVideo.html')

@app.route('/gameRun', methods=['GET', 'POST'])
def runGame():
    if request.method == 'POST':
        if 'first_init' in request.form:
            initial_theme = request.form['initial_theme']
            match initial_theme:
                case "fantasy":
                    init_dict = json.load(open("resources/fantasy.json"))
                    init_dict["available_npcs"] = FantasyNPCMap.MAP.keys()
                case "space":
                    init_dict = json.load(open("resources/space.json"))
                    init_dict["available_npcs"] = SpaceNPCMap.MAP.keys()
            context = Context(init_dict)
            response = first_prompt(context)
            context.update_context(response)
            
            # Queue video generation for initial response
            message_content = json.loads(response.choices[0].message.content)["story_output"]
            
            video_queue.put(("init", message_content))
            with open("video_queue.log", "a") as logfile:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logfile.write(f"[{current_time}] Queued initial video generation\n")
            
            return render_template('gameRun.html', context=context.get_context(), response=response.choices[0].message.content)
        
        elif 'game_loop' in request.form:
            context = Context(json.loads(request.form['context_dict']))
            user_input = request.form['player_input']
            response = prompt_gpt(user_input, context)
            context.update_context(response)
            
            # Queue video generation for each response
            message_content = json.loads(response.choices[0].message.content)["story_output"]
            
            video_queue.put(("game_loop", message_content))
            with open("video_queue.log", "a") as logfile:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logfile.write(f"[{current_time}] Queued game loop video generation\n")
            
            return render_template('gameRun.html', context=context.get_context(), response=response.choices[0].message.content)

    return render_template('gameRun.html', context='first_init' in request.form)

@app.route('/gameStart')
def startGame():
    return render_template('gameStart.html')

@app.route('/')
def home():
    return render_template('index.html')

# Cleanup function to stop workers gracefully
def cleanup_workers():
    # Signal all workers to stop
    for _ in range(MAX_WORKERS):
        video_queue.put(None)
    
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