from flask import Flask, send_from_directory, render_template
from flask import request, jsonify
from flask_cors import CORS

# import cv2
# import base64
# from PIL import Image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Разрешаем CORS для всех маршрутов


@app.route("/")
def dog():
    return render_template("index.html")


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
    print(data)
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=46578)
