from flask import Flask, request, jsonify, send_from_directory
from main import schedule_terp
import subprocess
import json

app = Flask(__name__)
import os

@app.route("/")
def index():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(current_directory, "static"), "index.html")

@app.route("/run_script", methods=["POST"])
def run_script():
    # input_data = request.form.get("input")

    # # Call the Python script and retrieve the output
    # command = ["/usr/local/bin/python3", "/Users/olivervillegas/ScheduleTerp/main.py"]
    # process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # output, _ = process.communicate(input=input_data.encode())

    # try:
    #     output_data = json.loads(output)
    # except json.JSONDecodeError:
    #     output_data = {"error": "Invalid output format"}

    # return jsonify(output_data)
    input_data = request.form.get("input")
    input_list = json.loads(input_data)  # Convert input data to a list

    schedules = schedule_terp(input_list)

    return jsonify(schedules)

if __name__ == "__main__":
    app.run()
