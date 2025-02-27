import cv2
import contextlib, os, logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO
import numpy as np
import json
from tqdm import tqdm

import subprocess

stop, start, pause = 0, 0, 0

# import eventlet
# import eventlet.wsgi


app = Flask(__name__)
socketio = SocketIO(app)
# socketio.init_app(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = "upload"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

criteria_data = {
    "emotional": {
        "name": "Эмоциональное состояние",
        "enabled": True,
        "score": 0,
        "max_score": 10,
        "sublevels": {
            "angry": {"score": 0, "max_score": 2},
            "disgust": {"score": 0, "max_score": 3},
            "fear": {"score": 0, "max_score": 5},
            "happy": {"score": 0, "max_score": 2},
            "sad": {"score": 0, "max_score": 3},
            "surprise": {"score": 0, "max_score": 5},
            "neutral": {"score": 0, "max_score": 5}
        },
    },
    "physical": {
        "name": "Физическое состояние",
        "enabled": True,
        "score": 0,
        "max_score": 100,
        "sublevels": {
            "pulse": {"score": 0, "max_score": 4},
            "breathing": {"score": 0, "max_score": 3},
            "blinking": {"score": 0, "max_score": 3},
        },
    },
    "seasonal": {
        "name": "Сезонность одежды",
        "enabled": True,
        "score": 0,
        "max_score": 5,
        "sublevels": {},
    },
    "subjective": {
        "name": "Субъективная оценка",
        "enabled": True,
        "score": 0,
        "max_score": 5,
        "sublevels": {},
    },
    "statistical": {
        "name": "Статистическая оценка",
        "enabled": False,
        "score": 0,
        "max_score": 5,
        "sublevels": {},
    },
    "result": {
        "name": "Результат",
        "enabled": True,
        "score": 0,
        "max_score": 100,
        "sublevels": {},
    }
}

data = {
    "gender": "Мужской",
    "age": 25,
    "departure": "Москва",
    "arrival": "Санкт-Петербург",
    "subjective_rating": 0,
    "question1text": "Как вы себя чувствуете?",
    "question1": "",
    "question2text": "Вопрос №2",
    "question2": ["1", "3"],  # Пример
    "criteria": criteria_data,
    "pulse_status": "Нормально",
    "breathing_status": "Средняя частота",
    "blinking_value": 15,
    "emotions": {"Счастье": 50, "Грусть": 20, "Гнев": 10, "Удивление": 20},
    "voice_emotions": {"Спокойствие": 60, "Стресс": 40},
}

users = {}

@app.route("/")
def index():
    return render_template("index.html", data="")

@app.route("/desktop")
def desktop():
    return render_template("desktop.html", data=data)
@app.route("/mobile")
def mobile():
    return render_template("mobile.html", data=data)
@app.route("/tablet")
def tablet():
    return render_template("tablet.html", data=data)
@app.route("/report")
def report():
    return render_template("report.html")
# @app.route("/auth")
# def auth():
#     return render_template("auth.html", data="")

@socketio.event
def connect():
    pass

def set_val(param, val):
    with open("Scripts/table_values.json", mode="r") as jf:
        dt = dict(json.load(jf))
    dt[param] = val
    with open("Scripts/table_values.json", mode="w") as jf:
        json.dump(dt, jf)

@app.route("/submit", methods=["POST"])
async def submit():
    user_data = request.json
    element = user_data.get("element")
    value = user_data.get("value")

    logging.info(f"Изменен элемент '{element}': значение = {value}")

    if element == 'subjective_rating':
        with open("Scripts/table_values.json", mode="r") as jf:
            dt = dict(json.load(jf))
        dt["subj"] = {}
        dt["subj"]["category"] = "subjective"
        dt["subj"]["score"] = value
        # last = max([0, 0] + [int(i) for i in dt])
        # dt[str(last+1)] = {"category": "subjective", "sublevel": {}, "score": str(value)}
        with open("Scripts/table_values.json", mode="w") as jf:
            json.dump(dt, jf)
    elif element == "start":
        set_val("start", True)
    elif element == "stop":
        set_val("stop", True)
    elif element == "pause":
        set_val("pause", True)

    if element in ["emotional", "physical", "seasonal", "subjective", "statistical", "result"]:
        enabled = bool(value)
        data[element] = enabled
        if element in criteria_data:
            criteria_data[element]["enabled"] = enabled
            # Если секция отключена, обнуляем все значения
            if not enabled:
                criteria_data[element]["score"] = 0
                for sublevel in criteria_data[element].get("sublevels", {}).values():
                    sublevel["score"] = 0
            socketio.emit("criteria_updated", criteria_data)
        return jsonify({"status": "success", "data": data})

    if element in data:
        data[element] = value
    elif element in ["genderSelect", "ageInput", "departureInput", "arrivalInput"]:
        if element == "genderSelect":
            data["gender"] = value
        elif element == "ageInput":
            with contextlib.suppress(ValueError):
                data["age"] = int(value)
        elif element == "departureInput":
            data["departure"] = value
        elif element == "arrivalInput":
            data["arrival"] = value
    elif element == "subjective_rating":
        with contextlib.suppress(ValueError):
            data["subjective_rating"] = int(value)
    elif element == "question1":
        data["question1"] = value
    elif element == "question2":
        data["question2"] = value
    print(criteria_data)
    return jsonify({"status": "success", "data": data})

@app.route("/upload", methods=["POST"])
def upload_file():
    # print(request.files)
    if "files" not in request.files:
        return "Файлы не были выбраны", 400

    files = request.files.getlist("files")
    for file in files:
        if file.filename:
            pth = os.path.join(app.config["UPLOAD_FOLDER"], "10.mp4")
            print(pth)
            file.save(pth)
            subprocess.Popen(["python", "gui/revised_2025/run_moduls.py"])
    return "Файлы успешно загружены"

@socketio.on("update_criteria")
def handle_criteria_update(update_data):  # sourcery skip: merge-repeated-ifs
    category = update_data.get("category")
    sublevel = update_data.get("sublevel")
    score = update_data.get("score")

    # Обновляем только если категория включена
    if category in criteria_data and criteria_data[category]["enabled"]:
        if sublevel:
            if sublevel in criteria_data[category]["sublevels"]:
                criteria_data[category]["sublevels"][sublevel]["score"] = score
        else:
            criteria_data[category]["score"] = score

        # Пересчитываем общий балл
        if sublevel:
            criteria_data[category]["score"] = sum(
                sub["score"] for sub in criteria_data[category]["sublevels"].values()
            )
        socketio.emit("criteria_updated", criteria_data)
        # eventlet.sleep(0.01)

# def translate_score():
#     while true:
#         new_predict_event.wait()
#         new_predict_event.clear()
#         predict = pred
#         update_data = {
#             "category": "physical",
#             "sublevel": "pulse",
#             "score": predict[1]
#         }
#         sio.emit("update_criteria", update_data)
# def get_pedict():
#     while True:
#         new_frame_event.wait()  # Ждем новый кадр
#         new_frame_event.clear()
#         frame = frame_array
#         # pulse, resp, blink = run_moduls(False, frame)
#         pred[1] = 1
#         pred[2] = 2
#         pred[3] = 3
#         new_predict_event.set()


@socketio.on('start_video')
def start_video():
    pass

def main():
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

main()