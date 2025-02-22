from flask import Flask, render_template, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def upload_form():
    return """
    <!doctype html>
    <html>
    <head><title>Загрузка файлов</title></head>
    <body>
        <h2>Выберите файлы для загрузки</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="files" multiple>
            <input type="submit" value="Загрузить">
        </form>
    </body>
    </html>
    """


@app.route("/upload", methods=["POST"])
def upload_file():
    if "files" not in request.files:
        return "Файлы не были выбраны", 400

    files = request.files.getlist("files")
    for file in files:
        if file.filename:
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
    return "Файлы успешно загружены"


if __name__ == "__main__":
    app.run(debug=True)
