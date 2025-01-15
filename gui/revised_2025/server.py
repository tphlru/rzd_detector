from flask import Flask, render_template, request, jsonify
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Статические данные (замените рыбой по необходимости)
data = {
    "gender": "Мужской",
    "age": 25,
    "departure": "Москва",
    "arrival": "Санкт-Петербург",
    "subjective_rating": 0,
    "question1": "Как вы себя чувствуете?",
    "question2": ["1", "3"],  # Пример выбранных значений
    "criteria": [
        {"name": "Статистическая оценка", "sublevel": 1, "points": 5, "total": 5},
    ],
    "pulse_status": "Нормально",
    "breathing_status": "Средняя частота",
    "blinking_value": 15,
    "emotions": {"Счастье": 50, "Грусть": 20, "Гнев": 10, "Удивление": 20},
    "voice_emotions": {"Спокойствие": 60, "Стресс": 40},
    "emotional": True,
    "physical": True,
    "seasonal": True,
    "subjective": True,
    "statistical": True,
}

@app.route("/")
def index():
    return render_template("index.html", data=data)

@app.route("/submit", methods=["POST"])
def submit():
    user_data = request.json
    element = user_data.get("element")
    value = user_data.get("value")

    # Логируем изменения
    logging.info(f"Изменен элемент '{element}': значение = {value}")

    # Обновляем данные на сервере
    if element in data:
        data[element] = value
    elif element in ["genderSelect", "ageInput", "departureInput", "arrivalInput"]:
        # Обработка полей "Данные"
        if element == "genderSelect":
            data["gender"] = value
        elif element == "ageInput":
            try:
                data["age"] = int(value)
            except ValueError:
                pass
        elif element == "departureInput":
            data["departure"] = value
        elif element == "arrivalInput":
            data["arrival"] = value
    elif element == "subjective_rating":
        try:
            data["subjective_rating"] = int(value)
        except ValueError:
            pass
    elif element == "question1":
        data["question1"] = value
    elif element == "question2":
        data["question2"] = value  # Ожидается список значений
    elif element in ["emotional", "physical", "seasonal", "subjective", "statistical"]:
        data[element] = bool(value)
    elif element == "reportButton":
        # Обработка нажатия кнопки "Показать отчет"
        pass  # Добавьте необходимую логику
    # Добавьте обработку других элементов по необходимости

    return jsonify({"status": "success", "data": data})

if __name__ == "__main__":
    app.run(debug=True)
    