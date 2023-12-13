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

app = Flask(__name__)
client = MongoClient('mongodb+srv://rzadwiptri:kelompok5@cluster0.sbzask3.mongodb.net/')
db = client['kelompokintel'] 

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
            return "Login berhasil" 
        else:
            return 'Login gagal. Periksa kembali email dan password Anda.'
    return render_template('login.html')

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)