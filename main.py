import json
import smtplib
import ssl
import psycopg2
from flask import Flask, render_template, request, flash, redirect
from datetime import datetime

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
        name TEXT,
        email VARCHAR(120),
        password VARCHAR(15),
        title VARCHAR(255),
        description TEXT,
        content TEXT,
        time TIMESTAMP);
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
    conn.commit()
    return redirect('/home')


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


@app.route('/home')
def home():
    try:
        cur.execute('SELECT * FROM POSTS;')
        posts = cur.fetchall()
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
        name = request.form.get('name')
        password = request.form.get('password')
        title = request.form.get('title')
        content = request.form.get('content')
        description = request.form.get('description')
        time = datetime.now()
        cur.execute("select id,fname,lname from users where email=%s and password=%s;", (email, password))
        user = cur.fetchone()
        if user is None:
            flash('Invalid email or password')
            return render_template('blog.html')
        cur.execute("INSERT INTO posts (name,email, password, title, description, content, time) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (name, email, password, title, description, content, time))
        conn.commit()
        print('Successfully inserted into posts')
    except Exception as ex:
        print('Could not insert to posts database', ex)
    return render_template('blog.html')


cur.execute("SELECT id, name, title, content, time FROM posts;")
posts = cur.fetchall()
conn.commit()


@app.route('/post/<int:post_id>')
def show_post(post_id):
    for post in posts:
        print(post)
        if post[0] == post_id:
            return render_template('post.html', title=post[2], content=post[3], name=post[1], time=post[4])
    return "Post not found"


app.run(debug=True)
cur.close()
conn.close()
