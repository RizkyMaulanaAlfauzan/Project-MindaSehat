from flask import (
    Flask, 
    render_template, 
    jsonify, 
    request, 
    session, 
    redirect,
    url_for
)   

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
    return render_template("buatJadwal.html")

@app.route('/registrasi', methods=['GET'])
def show_registration_page():
    return render_template('registrasi.html')

@app.route('/registrasi', methods=['POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if db.users.find_one({'name': name}):
            return 'Nama sudah digunakan, gunakan nama lain'

        db.users.insert_one({
            'name': name,
            'email': email,
            'password': password
        })
    
        return redirect('/login') 

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