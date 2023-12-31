# Basic Web Server (Flask)

from flask import Flask # pip install flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)