from flask import Flask, render_template, jsonify, request, current_app
from context import Context
import json
from openai import OpenAI
import openai
import os
from systemprompts import SystemPrompts
import sys
import datetime

app = Flask(__name__, template_folder='static/templates')
global context 

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

@app.route('/gameEnd')
def endGame():
    return render_template('gameEnd.html')

@app.route('/gameRun', methods=['GET','POST'])
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
            return render_template('gameRun.html', context=context.get_context(), response=response.choices[0].message.content)
        elif 'game_loop' in request.form:
            context = Context(json.loads(request.form['context_dict']))
            user_input = request.form['player_input']
            # with open("debug.log", "a") as logfile:
            #     logfile.write(f"Context at {datetime.datetime.now()}: {str(context.get_context())}\n")
            response = prompt_gpt(user_input, context)
            # with open("debug.log", "a") as logfile:
            #     logfile.write(f"Response at {datetime.datetime.now()}: {str(response)}\n")
            context.update_context(response)
            return render_template('gameRun.html', context = context.get_context(), response = response.choices[0].message.content)
        elif 'game_end' in request.form:
            return render_template('gameVideo.html', context = context.get_context())
        

    return render_template('gameRun.html', context = 'first_init' in request.form)
    

@app.route('/gameStart')
def startGame():
    return render_template('gameStart.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/howToPlay')
def howToPlay():
    return render_template('howToPlay.html')

if __name__ == '__main__':
    app.run(debug=True)