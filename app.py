from flask import Flask, render_template, jsonify, request, current_app
from context import Context
import json
from openai import OpenAI
import openai
import os

app = Flask(__name__, template_folder='static/templates')
global context

MODEL ="gpt-3.5-turbo"
MODEL_DEFINITION = {
    "role": "system",
    "content": 
    f"You are an assistant that is helping us to generate a dynamic storyline.
    You will be given the context of a story in JSON format.
    In the context: 
    - The player will have a status, location, and alive field;
    - The npcs will have a class, location, nature, status, and alive field;
    - The major story events will have a list of strings that describe the events that have occurred;
    - The complete story will be a string that describes the entire story;
    - The init_theme will have the initial_prompt and available_locations field;
    - The narrative_state will be one of the following: exposition, rising action, climax, falling action, and resolution;
    You will be given a user input and you will need to respond to the user input based on the context of the story. The way you
    continue the story should be reflective of the narrative state in order to keep the story advancing and following a narrative structure.
    The player should always die at the end of the story. This could be peaceful (happy ending) or violent (sad ending). This outcome
    depends on the player's input and choices.
    It is up to you to determine whether you should add a new NPC, update the player, change the locations of players or npcs.
    You should respond with the following:
    A JSON object with the following fields:
    - story_output: a string that describes the output of the continuation of the story.
    - context: a JSON object that is the exact same as the context given to you, but with the following changes:
        - player's status, location, and alive fields should be updated to reflect the new state of the player.
        - npcs' status, location, and alive fields should be updated to reflect the new state of the npcs.
        - major story events list should be updated to add the new story event.
        - complete story string should be updated to reflect the new state of the complete story.
        - narrative_state should be updated to reflect next narrative state.
    - added_npc: a JSON object that describes the newly created NPC with each of the fields populated.
    The story_output should be a string that is a a few sentences long. It should be a continuation of the story, but not the entire story.
    "
}

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
                case "scifi":
                    init_dict = json.load(open("resources/scifi.json"))
            context = Context(init_dict)
            return render_template('gameRun.html', context=context.get_context())
        elif 'game_loop' in request.form and 'context' in request.form:
            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
            )
            user_input = request.form['user_input']
            built_prompt = {
                "user_input": user_input,
                "current_context": context
            }
            chat_prompt = {
                "role": "user",
                "content": built_prompt
            }
            response = client.chat.completions.create(
                model=MODEL,
                messages=[MODEL_DEFINITION, chat_prompt]
            )
            context.update_context(response)
            return render_template('gameRun.html', context = context.get_context())
        elif 'game_end' in request.form:
            return render_template('gameVideo.html', context = context.get_context())
        

    return render_template('gameRun.html', context = 'first_init' in request.form)
    

@app.route('/gameStart')
def startGame():
    return render_template('gameStart.html')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)