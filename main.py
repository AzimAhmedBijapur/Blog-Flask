from flask import Flask, render_template
import json

app = Flask(__name__)

with open('config.json') as file:
    param = json.load(file)["params"]


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('sign-in.html')


app.run(debug=True)
