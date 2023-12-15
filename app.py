from flask import (
    Flask, 
    render_template, 
    jsonify, 
    request, 
    session, 
    redirect,
    url_for,
) 
from werkzeug.exceptions import BadRequestKeyError
  
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

client = MongoClient("mongodb+srv://rzadwiptri:kelompok5@cluster0.sbzask3.mongodb.net/?retryWrites=true&w=majority")  # Ganti URL dengan URL MongoDB Anda
db = client["db_mindasehat"]

app.config['TEMPLATES_AUTO_RELOAD'] = True

SECRET_KEY = "KELOMPOKLIMA"
TOKEN_KEY = "tokenkelompoklima"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/konsultasi")
def konsul():
    return render_template("konsultasi.html")

@app.route("/buatJadwal")
def buatJadwal():
    return render_template("buatJadwal.html")

@app.route("/sign-up")
def sign_up():
    msg = request.args.get("msg")
    return render_template("registrasi.html", msg=msg)

@app.route("/sign-up-user", methods=["POST"])  
def sign_up_user():
    theId = f"{uuid.uuid1()}"
    username_receive = request.form["name"]
    email_receive = request.form["email"]
    email_info = db.user.find_one({"email": email_receive})
    password_receive = request.form["password"]
    confirm_password_receive = request.form["confirm_password"]
    if email_info:
        return redirect(url_for("sign_up", msg="Email Sudah Terdaftar"))
    if len(password_receive) < 8:
        return redirect(url_for("sign_up", msg="Password Terlalu Pendek"))
    if password_receive != confirm_password_receive:
        return redirect(url_for("sign_up", msg="Password Tidak valid"))
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    doc = {
        "uuid": theId,
        "username": username_receive,
        "email": email_receive,
        "password": password_hash, 

   }
    db.user.insert_one(doc)
    # return jsonify({"result": "success"})
    return redirect(url_for("login", msg="Silahkan Login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email_receive = request.form["email_give"]
        password_receive = request.form["password_give"]
        pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
        role = request.form["role_give"]
        if role == "user":
            namespace = db.user
        elif role == "psikolog":
            namespace = db.psikolog
        else:
            return jsonify(
                {
                    "result": "fail",
                    "msg": "Pilih role dengan benar",
                }
            )
        result = namespace.find_one(
            {
                "email": email_receive,
                "password": pw_hash,
            }
        )
        if result:
            payload = {
                "id": email_receive,
                "role": role,
                # the token will be valid for 24 hours
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return jsonify({"result": "success", "token": token, "role": role})

        else:
            return jsonify(
                {
                    "result": "fail",
                    "msg": "Email atau password salah",
                }
            )

    token_receive = request.cookies.get(TOKEN_KEY)
    if token_receive:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        
            # Redirect sesuai peran setelah berhasil login
        if role == "user":
            return redirect(url_for("home"))  # Ganti "home" dengan rute yang sesuai untuk pengguna
        elif role == "psikolog":
            return redirect(url_for("psikolog"))  # Ganti "edit_konsultasi" dengan rute yang sesuai untuk psikolog
        else:
            return jsonify({"result": "fail", "msg": "Email atau password salah"})
    return render_template("login.html")    


@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/psikolog")
def psikolog():
    return render_template("psikolog.html",)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)