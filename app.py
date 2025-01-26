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

app = Flask(__name__, template_folder='static/templates')
global context 

# Create a queue for video generation requests
video_queue = queue.Queue()

def video_generation_worker():
    while True:
        prompt_text = video_queue.get()
        if prompt_text is None:  # Exit signal
            break
        generate_video(prompt_text)  # Call your video generation function
        video_queue.task_done()

# Start the video generation worker thread
threading.Thread(target=video_generation_worker, daemon=True).start()

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
                case "space":
                    init_dict = json.load(open("resources/space.json"))
            context = Context(init_dict)
            response = first_prompt(context)
            context.update_context(response)
            return render_template('gameRun.html', context=context.get_context(), response=response.choices[0].message.content, hasNPC=True)
        
        elif 'game_loop' in request.form:
            context = Context(json.loads(request.form['context_dict']))
            user_input = request.form['player_input']
            response = prompt_gpt(user_input, context)
            context.update_context(response)

            # Get the narrator's text for video generation
            narrator_text = response.choices[0].message.content
            video_queue.put(narrator_text)  # Add the narrator text to the video generation queue

            return render_template('gameRun.html', context=context.get_context(), response=narrator_text, hasNPC=True)

        elif 'game_end' in request.form:
            return render_template('gameVideo.html', context=context.get_context())

    return render_template('gameRun.html', context='first_init' in request.form)
    

@app.route('/gameStart')
def startGame():
    return render_template('gameStart.html')

@app.route('/')
def home():
    return render_template('index.html')

# To stop the video generation worker when the application exits
atexit.register(lambda: video_queue.put(None))  # Send exit signal to the worker

if __name__ == '__main__':
    app.run(debug=True)