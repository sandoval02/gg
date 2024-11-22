import os
from flask import Flask, jsonify, render_template


app = Flask(__name__)
application = app


@app.route('/')
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)