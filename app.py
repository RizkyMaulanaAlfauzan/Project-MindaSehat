from flask import (
    Flask, 
    render_template, 
    jsonify, 
    request, 
    session, 
    redirect,
    url_for
)   

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("buatJadwal.html")

@app.route('/registrasi', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return "Password dan konfirmasi password tidak cocok. Silakan coba lagi."
        return "Registrasi berhasil untuk nama: {}, email: {}".format(nama, email)
    return render_template('registrasi.html')

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