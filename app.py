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

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app.config['TEMPLATES_AUTO_RELOAD'] = True

SECRET_KEY = "KELOMPOKLIMA"
TOKEN_KEY = "tokenkelompoklima"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def homeAfter():
    token_receive = request.cookies.get(TOKEN_KEY)
    
    msg = request.args.get("msg")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        if user_info:
            role = user_info["role"]
            return render_template("home.html", role=role,  msg=msg)
        return redirect(url_for("login"))

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="Your token has expired"))
        
@app.route("/pakar")
def pakar():
    token_receive = request.cookies.get(TOKEN_KEY)
    psikolog = db.user.find_one({"role":"psikolog"})
    msg = request.args.get("msg")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        if user_info:
            role = user_info["role"]
            return render_template("pakarPsikolog.html", role=role,psikolog=psikolog,  msg=msg)
        return redirect(url_for("login"))

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return render_template("pakarPsikolog.html",psikolog=psikolog, role='viewer',  msg=msg)

    

@app.route("/konsultasi")
def konsul():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        psikolog = db.user.find_one({"role":"psikolog"})
        jadwal = db.jadwal.find()
        if user_info["role"] == 'user':
            jadwal = db.jadwal.find({"username": user_info["username"]})
        if user_info:
            msg = request.args.get("msg")
            return render_template("konsultasiPsikolog.html", user_info=user_info,psikolog=psikolog, jadwal=jadwal,  msg=msg)
        return redirect(url_for("login"))

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))
    

@app.route("/ubahStatus", methods=['POST'])
def ubahStatus():
    if request.method == "POST":
        token_receive = request.cookies.get(TOKEN_KEY)
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            # We should create a new post here           
            
            status = request.form.get('status')
            idnya = request.form.get('idnya')
            
            doc = {                
                "status" : status,                
            }

            db.jadwal.update_one({"uuid": idnya}, {"$set": doc})
            return jsonify({"result": "success", "msg": "Ubah Status successful!"})
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("home"))
        
@app.route("/simpanAlasan", methods=['POST'])
def simpanAlasan():
    if request.method == "POST":
        token_receive = request.cookies.get(TOKEN_KEY)
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            # We should create a new post here           
            
            alasan = request.form.get('alasan')
            idnya = request.form.get('idnya')
            
            doc = {                
                "alasan" : alasan,                
            }

            db.jadwal.update_one({"uuid": idnya}, {"$set": doc})
            return jsonify({"result": "success", "msg": "Alasan successful!"})
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("home"))
        
@app.route("/buatJadwal", methods=['GET','POST'])
def buatJadwal():
    if request.method == "POST":
        token_receive = request.cookies.get(TOKEN_KEY)
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            # We should create a new post here
            user_info = db.user.find_one({"email": payload["id"]})
            tempat_konsul = request.form.get('tempatKonsul')
            konsul_date = request.form.get('date')
            waktu_konsul = request.form.get('waktuKonsul')
            theId = f"{uuid.uuid1()}"
            doc = {
                "uuid": theId,
                "username": user_info["username"],
                "tempat_konsul": tempat_konsul,
                "konsul_date" : konsul_date,
                "waktu_konsul": waktu_konsul,
                "status" : "pending",
                "alasan" : " "
            }

            db.jadwal.insert_one(doc)
            return jsonify({"result": "success", "msg": "Buat jadwal successful!"})
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("home"))
    # GET
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        psikolog = db.user.find_one({"role":"psikolog"})
        if user_info:
            msg = request.args.get("msg")
            return render_template("buatJadwal.html", user_info=user_info,psikolog=psikolog,  msg=msg)
        return redirect(url_for("login"))

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))
    

@app.route("/sign-up")
def sign_up():
    msg = request.args.get("msg")
    return render_template("registrasi.html", msg=msg)

@app.route("/sign-up-user", methods=["POST"])  
def sign_up_user():    
    username_receive = request.form["name"]
    email_receive = request.form["email"]
    akun_info = db.user.find_one({"$or": [{"email":email_receive},{"username":username_receive}]})
    password_receive = request.form["password"]
    confirm_password_receive = request.form["confirm_password"]

    if akun_info:
        return redirect(url_for("sign_up", msg="Nama / Email Sudah Terdaftar"))
    # Periksa apakah kata sandi dan konfirmasi kata sandi cocok
    if password_receive != confirm_password_receive:
        return redirect(url_for("sign_up", msg="Password Tidak valid"))
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    # Simpan data pengguna ke database
    doc = {        
        "username": username_receive,
        "email": email_receive,
        "password": password_hash,
        "role" : "user"
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
        
        result = db.user.find_one(
            {
                "email": email_receive,
                "password": pw_hash,
            }
        )
        if result:
            if result["role"] == "user":
                role = "user"
            else :
                role = "psikolog"
                
            payload = {
                "id": email_receive,
                "role": role,
                # the token will be valid for 24 hours
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return jsonify({"result": "success", "token": token})

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
        return redirect(url_for("homeAfter"))        
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)