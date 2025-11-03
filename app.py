from flask import Flask, render_template
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run-simulator")
def run_simulator():
    # Adjust the path to your Python file
    script_path = os.path.join(os.getcwd(), "launcher.py")
    subprocess.Popen(["python", script_path])
    return render_template("running.html")

if __name__ == "__main__":
    app.run(debug=True)