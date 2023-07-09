import json
import smtplib
import ssl
import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)

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
        email VARCHAR(120),
        password VARCHAR(15)
        );
    """)
    conn.commit()
    print('Successfully created table users')
except Exception as e:
    print('Error creating table users', e)

# routes


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form.get('email')
    password = request.form.get('password')
    print("select id from users where email=%s and password=%s;", (email, password))
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
        print("INSERT INTO users (fname, lname, email, password) VALUES (%s,%s,%s,%s)",
                    (fname, lname, email, password))
        cur.execute("INSERT INTO users (fname, lname, email, password) VALUES (%s,%s,%s,%s)",
                    (fname, lname, email, password))
        conn.commit()
        print('Successfully inserted to users')
    except Exception as e:
        print('Could not insert to users', e)
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html', name="A blog for programmers by programmers")


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


@app.route('/blog')
def blog():
    return render_template('blog.html')


app.run(debug=True)
cur.close()
conn.close()
