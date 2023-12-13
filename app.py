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



if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)