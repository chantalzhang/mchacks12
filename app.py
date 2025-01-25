from flask import Flask, render_template, jsonify, request

app = Flask(__name__, template_folder='static/templates')
game_instance = None

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)