from flask import Flask, render_template, request
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


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/contact/us', methods=['POST', 'GET'])
def contactus():
    if request.method == 'POST':
        return 'HEY'


app.run(debug=True)
