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
        if 'first_init' in request.form:
            initial_theme = request.form['initial_theme']
            match initial_theme:
                case "fantasy":
                    init_dict = json.load(open("resources/fantasy.json"))
                case "scifi":
                    init_dict = json.load(open("resources/scifi.json"))
            context = Context(init_dict)
            return render_template('gameRun.html', context=context.get_context())
        elif 'game_loop' in request.form:
            #gameloop
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