import cv2

import contextlib, os, logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO
import numpy as np
from flask_login import login_user, LoginManager, UserMixin, current_user, login_required
from hashlib import sha256
import json

class User(UserMixin):
    def __init__(self, user_id, name, org):
        self.id = user_id
        self.org = org
        self.name = name
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    def get_id(self,user_id):
        return self.id, sesf.org, self.name

# @LoginManager.user_loader
# def load_user(login,name,org):
#     return User.get(login)
import eventlet
import eventlet.wsgi


mode = "dev"  # "dev" or "prod"

app = Flask(__name__)
# app.secret_key = 'abvgd'  
# login_manager = LoginManager()
# login_manager.init_app(app)
socketio = SocketIO(app, async_mode="eventlet")

FRAME_SHAPE = (1080, 1920, 3)
FRAME_DTYPE = np.uint8
HSD_IP = "192.168.0.102"

frame_var = None
# with open(r"C:\Users\kvant_08\Documents\GitHub\rzd_detector\gui\revised_2025\users.json","r+",encoding="utf-8") as file:
#     users = dict(json.load(file))

# @login_manager.user_loader
# def load_user(user_id):
#     user = User(users[user_id], users[user_id][name], users[user_id][org])
#     print(user_id)
#     return users[user_id]

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
            "happiness": {"score": 0, "max_score": 2},
            "stress": {"score": 0, "max_score": 3},
            "anxiety": {"score": 0, "max_score": 5},
        },
    },
    "physical": {
        "name": "Физическое состояние",
        "enabled": True,
        "score": 0,
        "max_score": 10,
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

# @socketio.on("login")
# def login(data):
#     print(data)

# @socketio.on("register")
# def register(data):
#     print(data)
# warning example

# @socketio.event
# def connect():
#     socketio.emit("warning","warning text")


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
        print(dt["subj"])
        # last = max([0, 0] + [int(i) for i in dt])
        # dt[str(last+1)] = {"category": "subjective", "sublevel": {}, "score": str(value)}
        with open("Scripts/table_values.json", mode="w") as jf:
            json.dump(dt, jf)


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
    if "files" not in request.files:
        return "Файлы не были выбраны", 400

    files = request.files.getlist("files")
    for file in files:
        if file.filename:
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
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
        eventlet.sleep(0.01)

# @app.route('/auth', methods=['GET', 'POST'])
# def auth():
#     if request.method == 'POST':
#         if request.form["passwd1"]==request.form["passwd2"]:
#             passCache = sha256(request.form["passwd1"].encode('utf-8')).hexdigest()
#             user = User(str(request.form["login"]), str(request.form["name"]), str(request.form["org"])) 
#             users[str(request.form["login"])] = {"pass":str(passCache),"org":request.form["org"],"name":request.form["name"],}
#             login_user(user)
#             with open(r"C:\Users\kvant_08\Documents\GitHub\rzd_detector\gui\revised_2025\users.json","w+",encoding="utf-8") as file:
#                 file.write(json.dumps(users, indent=4))
#             return redirect(url_for('desktop'))
#     return render_template("auth.html")

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

# async def generate_stream():
#     """Асинхронная функция для генерации потока видео"""
#     client = WHEPClient(get_hsd_camera_url(HSD_IP))
#     await client.connect()
#     while True:
#         frame = await client.get_raw_frame()
#         frame = crop_face(frame)
#         global frame_array
#         frame_array[:] = np.array( dtype=FRAME_DTYPE)
#         new_frame_event.set()
#         await asyncio.sleep(0.03)  # Небольшая задержка для уменьшения нагрузки


# @socketio.on('start_video')
# def start_video():
#     print("aa")
#     socketio.start_background_task(generate_stream)

def main():
    # generate = mp.Process(target=asyncio.run(generate_stream()))
    # generate.start()
    # predict = mp.Process(target=get_pedict)
    # predict.start()
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True, debug=True)

main()