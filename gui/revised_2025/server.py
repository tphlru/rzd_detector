import contextlib, os, logging
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

mode = "dev"  # "dev" or "prod"

app = Flask(__name__)
socketio = SocketIO(app)

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
}

data = {
    "gender": "Мужской",
    "age": 25,
    "departure": "Москва",
    "arrival": "Санкт-Петербург",
    "subjective_rating": 0,
    "question1": "Как вы себя чувствуете?",
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


@app.route("/submit", methods=["POST"])
def submit():
    user_data = request.json
    element = user_data.get("element")
    value = user_data.get("value")

    logging.info(f"Изменен элемент '{element}': значение = {value}")

    if element in ["emotional", "physical", "seasonal", "subjective", "statistical"]:
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


if __name__ == "__main__":
    if mode == "dev":
        socketio.run(app, debug=True, port=5000)
