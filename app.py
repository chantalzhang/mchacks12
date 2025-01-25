from flask import Flask, render_template, jsonify, request, current_app
from context import Context
import json

app = Flask(__name__, template_folder='static/templates')
global context


@app.route('/gameEnd')
def endGame():
    return render_template('gameEnd.html')

@app.route('/gameRun', methods=['GET','POST'])
def runGame():
    if request.method == 'POST':
        initial_theme = request.form['initial_theme']
        match initial_theme:
            case "medieval":
                init_dict = json.load(open("resources/medieval.json"))
            case "scifi":
                init_dict = json.load(open("resources/scifi.json"))
        context = Context(init_dict)
    
    return render_template('gameRun.html', context=context.get_context())
    

@app.route('/gameStart')
def startGame():
    return render_template('gameStart.html')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)