from flask import (
    Flask, 
    render_template, 
    jsonify, 
    request, 
    session, 
    redirect,
    url_for
) 
  
import uuid
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from os.path import join, dirname

app = Flask(__name__)


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app.config['TEMPLATES_AUTO_RELOAD'] = True

SECRET_KEY = "KELOMPOKLIMA"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/konsultasi")
def konsul():
    return render_template("konsultasi.html")

@app.route("/buatJadwal")
def buatJadwal():
    return render_template("home/buatJadwal.html")

@app.route("/sign-up")
def sign_up():
    msg = request.args.get("msg")
    return render_template("registrasi.html", msg=msg)

@app.route("/sign_up/user", methods=["POST"])
def sign_up_user():
    theId = f"{uuid.uuid1()}"
    username_receive = request.form["name"]
    email_receive = request.form["email"]
    email_info = db.user.find_one({"email": email_receive})
    password_receive = request.form["password"]
    confirm_password_receive = request.form["confirm_password"]
    if email_info:
        return redirect(url_for("sign_up", msg="Email Anda Sudah Terdaftar"))
    if len(password_receive) < 8:
        return redirect(url_for("sign_up", msg="Password Anda Terlalu Pendek"))
    if password_receive != confirm_password_receive:
        return redirect(url_for("sign_up", msg="Password Anda Tidak valid, Mohon di cek kembali!!!"))
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    doc = {
        "uuid": theId,
        "username": username_receive,
        "email": email_receive,
        "password": password_hash,  # password
    }
    db.user.insert_one(doc)
    # return jsonify({"result": "success"})
    return redirect(url_for("login", msg="Silahkan Login"))


@app.route("/sign_up/psikologis", methods=["POST"])
def sign_up_psikologis():
    theId = f"{uuid.uuid1()}"
    username_receive = request.form["name"]
    email_receive = request.form["email"]
    email_info = db.psikologis.find_one({"email": email_receive})
    password_receive = request.form["password"]
    confirm_password_receive = request.form["confirm_password"]
    if email_info:
        return redirect(url_for("sign_up", msg="Email Anda Sudah Terdaftar"))
    if len(password_receive) < 8:
        return redirect(url_for("sign_up", msg="Password Anda Terlalu Pendek"))
    if password_receive != confirm_password_receive:
        return redirect(url_for("sign_up", msg="Password Anda Tidak valid, Mohon di cek kembali!!!"))
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    doc = {
        "uuid": theId,
        "username": username_receive,
        "email": email_receive,
        "password": password_hash,  # password
    }
    db.psikologis.insert_one(doc)
    # return jsonify({"result": "success"})
    return redirect(url_for("login", msg="Silahkan Login"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in [email] == password:
            return redirect(url_for('home'))
        else:
            return 'Login gagal. Periksa kembali email dan password Anda.'
    return render_template('login.html')

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)