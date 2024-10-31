from flask import Flask, send_from_directory, render_template, Response
from flask import request, jsonify, redirect
from flask_cors import CORS

import gui_controller
import requests

import cv2
import numpy as np
import subprocess
import time

# import base64
# from PIL import Image


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Разрешаем CORS для всех маршрутов

@app.route("/")
def dog():
    return render_template("index.html")

@app.route("/audio-input")
def mic():
    # start listener
    try:
        # subprocess.Popen(["/home/stimur/miniforge3/envs/ti/bin/python", "/home/timur/Projects/rzd_detector/gui/dev/web-server/microphone_loader/server.py"])
        time.sleep(0.5)
    except OSError:
        print("Microphone listener already started")
    return redirect("http://localhost:8888", code=302) 

@app.route("/mobile")
def mob():
    return render_template("ind2.html")


# Route to serve static files from the 'package' directory
@app.route("/package/<path:filename>")
def serve_package_files(filename):
    return send_from_directory("package", filename)


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    if not data.get("value").isascii():
        data["value"] = data["value"].encode().decode()
    ids = {
        "next": gui_controller.next_client,
        "reset": gui_controller.reset,
        "stop": gui_controller.stop,
        "info": gui_controller.info,
        "Device_accept": gui_controller.Device_accept,
        "Camera_accept": gui_controller.Camera_accept,
        "Micro_accept": gui_controller.Micro_accept,
        "overall_quest_m2": gui_controller.overall_quest_m2,
        "overall_quest_m1": gui_controller.overall_quest_m1,
        "overall_quest_0": gui_controller.overall_quest_0,
        "overall_quest_p1": gui_controller.overall_quest_p1,
        "second_quest_1": gui_controller.second_quest_1,
        "second_quest_2": gui_controller.second_quest_2,
        "second_quest_3": gui_controller.second_quest_3,
        "second_quest_4": gui_controller.second_quest_4,
        "first_quest": gui_controller.first_quest,
        "there": gui_controller.there,
        "here": gui_controller.here,
        "age": gui_controller.age,
        "gender": gui_controller.gender
    }
    if data.get("id") != None:
        changed_ids =["here", "age", "gender", "there", "here", "Device_accept", "Camera_accept", "Micro_accept", "first_quest"]
        if data.get("id") in changed_ids:
            ids[data.get("id")](data.get("value"))
        elif data.get("id") not in changed_ids:
            ids[data.get("id")]()
    print(data)
    return jsonify(data)



def run():
    app.run(host="0.0.0.0", port=46578)

if __name__ == "__main__":
    run()
