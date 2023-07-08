from flask import Flask, render_template, request
import json
import MySQLdb

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

local = True

with open('config.json') as file:
    param = json.load(file)["params"]

if local:
    app.config['SQLALCHEMY_DATABASE_URI'] = param['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = param['production_uri']


userdb = SQLAlchemy(app)


class User(userdb.Model):
    sno = userdb.Column(userdb.Integer, primary_key=True)
    fname = userdb.Column(userdb.String(80))
    lname = userdb.Column(userdb.String(80))
    email = userdb.Column(userdb.String(120), unique=True)
    password = userdb.Column(userdb.String(15), unique=True)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email, password=password).first()
    user_exists = bool(User.query.filter_by(email=email, password=password).first())
    if user_exists:
        return render_template('home.html', name="Welcome "+user.fname+" "+user.lname)
    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('sign-in.html')

    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    new_user = User(fname=fname, lname=lname, email=email, password=password)
    userdb.session.add(new_user)
    userdb.session.commit()
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html', name="A blog for programmers by programmers")


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/contact/us', methods=['POST', 'GET'])
def contactus():
    if request.method == 'POST':
        return 'HEY'


@app.route('/blog')
def blog():
    return render_template('blog.html')


app.run(debug=True)
