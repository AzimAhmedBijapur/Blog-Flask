import json
import smtplib
import ssl
import psycopg2
from io import BytesIO
from PIL import Image
from flask import Flask, render_template, request, flash, redirect
import base64
import os
import imghdr
from uuid import uuid1
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
local = True

with open('config.json') as file:
    param = json.load(file)["params"]


# postgresql db
try:
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1234", port=5432)
    print('Connection Successful')
except Exception as e:
    print('Connection Failed', e)

cur = conn.cursor()

try:
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        id serial PRIMARY KEY,
        fname TEXT,
        lname TEXT,
        email VARCHAR(120) UNIQUE,
        password VARCHAR(15)
        );
    """)
    conn.commit()
    print('Successfully created table users')
except Exception as e:
    print('Error creating table users', e)

try:
    cur.execute("""CREATE TABLE IF NOT EXISTS posts(
        id serial PRIMARY KEY,
        email VARCHAR(120),
        password VARCHAR(15),
        title VARCHAR(255),
        content TEXT,
        img BYTEA)
    """)
    conn.commit()
    print('Successfully created table posts')
except Exception as e:
    print('Error creating table posts', e)


# routes


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form.get('email')
    password = request.form.get('password')
    cur.execute("select id,fname,lname from users where email=%s and password=%s;", (email, password))
    user = cur.fetchone()
    if user is None:
        return render_template('login.html')
    fname = user[1]
    lname = user[2]
    conn.commit()
    return render_template('home.html', name=f"Welcome {fname} {lname}")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('sign-in.html')

    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        cur.execute("INSERT INTO users (fname, lname, email, password) VALUES (%s,%s,%s,%s) "
                    "ON CONFLICT (email) DO NOTHING;",
                    (fname, lname, email, password))
        conn.commit()
        print('Successfully inserted to users')
    except Exception as ex:
        print('Could not insert to users', ex)
    return render_template('login.html')


def get_format(bytea):
    # decoded_string = bytes(base64.b64encode(bytea).decode('utf-8'))
    encoded_bytes = bytes(bytea)
    extension = imghdr.what(None, h=encoded_bytes)
    return extension


def decode_bytea(bytea):
    return base64.b64encode(bytea).decode('utf-8')


app.jinja_env.filters.update(get_format=get_format)


app.jinja_env.filters.update(decode_bytea=decode_bytea)


@app.route('/home')
def home():
    try:
        cur.execute('SELECT * FROM POSTS;')
        posts = cur.fetchall();
        conn.commit()
    except Exception as ex:
        print('Could not fetch from the db', ex)
    return render_template('home.html', name="A blog for programmers by programmers", posts=posts)


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    email = request.form.get('email')
    password = request.form.get('password')
    sub = request.form.get('subject')
    msg = request.form.get('msg')
    port = 465
    context = ssl.create_default_context()
    message = 'Subject: {}\n\n{}'.format(sub, msg)
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        if local:
            server.login(email, param['app_password'])
        else:
            server.login(email, password)
        server.sendmail(email, 'whalefry@gmail.com', message)
    return render_template('contact.html')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'GET':
        return render_template('blog.html')
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        title = request.form.get('title')
        content = request.form.get('content')
        img = request.files['img']
        img_file = img.read()
        encoded_image = base64.b64encode(img_file)
        cur.execute("select id,fname,lname from users where email=%s and password=%s;", (email, password))
        user = cur.fetchone()
        if user is None:
            flash('Invalid email or password')
            return render_template('blog.html')
        cur.execute("INSERT INTO posts (email, password, title, content, img) VALUES (%s, %s, %s, %s, %s);",
                    (email, password, title, content, encoded_image))
        conn.commit()
        print('Successfully inserted into posts')
    except Exception as ex:
        print('Could not insert to posts database',ex)
    return render_template('blog.html')


app.run(debug=True)
cur.close()
conn.close()
