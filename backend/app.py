from flask import Flask

app = Flask(__name__)

@app.route("/preimage")
def preimage():
    return "<p>preimage</p>"