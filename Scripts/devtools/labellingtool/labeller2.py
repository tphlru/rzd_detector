import subprocess
import sys
import importlib.util
import tkinter as tk
from tkinter import messagebox
import os
import time
import csv
import random
import json
from functools import partial

REQUIRED_PACKAGES = ["PyQt6", "matplotlib", "pynput"]


def check_and_install_dependencies():
    if missing_packages := [
        pkg for pkg in REQUIRED_PACKAGES if importlib.util.find_spec(pkg) is None
    ]:
        root = tk.Tk()
        root.withdraw()
        msg = f"Отсутствуют следующие пакеты: {', '.join(missing_packages)}.\n\nПопробую установить..."
        messagebox.showwarning("Установка зависимостей", msg)

        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError:
                messagebox.showerror(
                    "Ошибка установки",
                    f"Не удалось установить {package}. Установите вручную и перезапустите программу.",
                )
                sys.exit(1)

        messagebox.showinfo(
            "Перезапуск", "Все зависимости установлены. Перезапустите программу."
        )
        sys.exit(0)


check_and_install_dependencies()
5
from PyQt6.QtWidgets import (  # noqa: E402
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QGridLayout,
    QInputDialog,
    QDialog,
    QVBoxLayout,
    QCheckBox,
    QScrollArea,
)
from PyQt6.QtGui import QPixmap, QKeySequence  # noqa: E402
from PyQt6.QtCore import Qt, QEvent  # noqa: E402
from pynput import keyboard  # noqa: E402
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


LABELS = ["1", "2", "3", "4"]
SAVE_FILE = "annotations.csv"
SKIP_FILE = "skipped.txt"
LAST_DIR_FILE = "last_directory.txt"
CONFIG_FILE = "hotkeys_config.json"


class HotkeyConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        self.hotkeys = {}
        self.listening_button = None
        self.load_config()

    def initUI(self):
        self.setWindowTitle("Настройка горячих клавиш")
        self.setGeometry(200, 200, 400, 500)

        layout = QVBoxLayout()

        # Global hotkeys checkbox
        self.global_hotkeys_cb = QCheckBox("Глобальные горячие клавиши", self)
        self.global_hotkeys_cb.setChecked(False)
        layout.addWidget(self.global_hotkeys_cb)

        # Scroll area for buttons
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.buttons_layout = QVBoxLayout(scroll_widget)

        # Create config rows for each label
        self.button_configs = {}
        for label in LABELS + ["skip"]:
            row = QWidget()
            row_layout = QHBoxLayout(row)

            # Visibility checkbox
            vis_cb = QCheckBox(f"Показывать кнопку {label}", row)
            vis_cb.setChecked(True)

            # Hotkey button
            hotkey_btn = QPushButton("Нет клавиши", row)
            hotkey_btn.clicked.connect(partial(self.start_listening, label, hotkey_btn))

            row_layout.addWidget(vis_cb)
            row_layout.addWidget(hotkey_btn)

            self.button_configs[label] = {"visible": vis_cb, "hotkey": hotkey_btn}
            self.buttons_layout.addWidget(row)

        scroll_widget.setLayout(self.buttons_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Save button
        save_btn = QPushButton("Сохранить", self)
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def start_listening(self, label, button):
        if self.listening_button:
            self.listening_button.setStyleSheet("")

        self.listening_button = button
        button.setText("Нажмите клавишу...")
        button.setStyleSheet("background-color: yellow")
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if self.listening_button and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            key_text = QKeySequence(key).toString()
            self.hotkeys[self.listening_button] = key
            self.listening_button.setText(f"Клавиша: {key_text}")
            self.listening_button.setStyleSheet("")
            self.listening_button = None
            return True
        return super().eventFilter(obj, event)

    def save_config(self):
        config = {"global_hotkeys": self.global_hotkeys_cb.isChecked(), "buttons": {}}

        for label, widgets in self.button_configs.items():
            config["buttons"][label] = {
                "visible": widgets["visible"].isChecked(),
                "hotkey": widgets["hotkey"].text(),
            }

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

        self.parent.apply_hotkey_config(config)
        self.accept()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return

        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        self.global_hotkeys_cb.setChecked(config.get("global_hotkeys", False))

        for label, settings in config.get("buttons", {}).items():
            if label in self.button_configs:
                self.button_configs[label]["visible"].setChecked(
                    settings.get("visible", True)
                )
                self.button_configs[label]["hotkey"].setText(
                    settings.get("hotkey", "Нет клавиши")
                )


class ImageLabelingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.hotkey_listener = None
        self.initUI()
        self.loadProgress()
        self.load_hotkey_config()

    def initUI(self):
        self.setWindowTitle("Image Labeling Tool")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btns = []
        self.layout = QGridLayout()

        # Split Dataset Button
        self.split_btn = QPushButton("Разбить датасет", self)
        self.split_btn.clicked.connect(self.split_dataset)
        self.layout.addWidget(self.split_btn, 0, 0, 1, 1)

        # Add Hotkey Config Button
        self.hotkey_btn = QPushButton("Установить hotkeys", self)
        self.hotkey_btn.clicked.connect(self.show_hotkey_config)
        self.layout.addWidget(self.hotkey_btn, 0, 1, 1, 1)

        # Image Display
        self.layout.addWidget(self.image_label, 1, 0, 2, 4)

        # Classification Buttons
        btn_layout = QHBoxLayout()
        for label in LABELS:
            btn = QPushButton(label, self)
            btn.clicked.connect(lambda checked, lbl=label: self.annotate(lbl))
            btn_layout.addWidget(btn)
            self.btns.append(btn)

        self.skip_btn = QPushButton("Пропустить", self)
        self.skip_btn.clicked.connect(self.skip_image)
        btn_layout.addWidget(self.skip_btn)

        self.layout.addLayout(btn_layout, 3, 0, 1, 4)

        # Stats Display
        self.stats_label = QLabel("Статистика: ", self)
        self.layout.addWidget(self.stats_label, 4, 0, 1, 4)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(
            self.canvas, 1, 4, 2, 1
        )  # Перемещение в правый верхний угол
        self.canvas.setFixedWidth(
            self.width() // 5 + 30
        )  # Уменьшение ширины гистограммы

        self.setLayout(self.layout)

        self.image_files = []
        self.current_index = 0
        self.annotations = {}
        self.skipped = set()
        self.start_time = time.time()
        self.processed_count = 0

        self.load_images()
        self.show_next_image()

    def split_dataset(self):
        n_splits, ok = QInputDialog.getInt(
            self, "Разбиение датасета", "Введите количество выборок:", 2, 2, 100
        )
        if not ok:
            return

        seed_value, ok = QInputDialog.getInt(
            self, "Введите seed", "Введите seed для воспроизводимости:", 42, 0, 10000
        )
        if not ok:
            return

        random.seed(seed_value)
        random.shuffle(self.image_files)

        base_dir = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сохранения выборок"
        )
        if not base_dir:
            return

        split_size = len(self.image_files) // n_splits
        for i in range(n_splits):
            split_folder = os.path.join(base_dir, f"split_{i+1}")
            os.makedirs(split_folder, exist_ok=True)
            split_files = self.image_files[i * split_size : (i + 1) * split_size]
            for file in split_files:
                os.rename(file, os.path.join(split_folder, os.path.basename(file)))

        QMessageBox.information(self, "Готово", "Разбиение датасета завершено!")

    def load_images(self):
        last_dir = None
        if os.path.exists(LAST_DIR_FILE):
            with open(LAST_DIR_FILE, "r") as f:
                last_dir = f.read().strip()

        if (
            last_dir
            and QMessageBox.question(
                self,
                "Использовать предыдущий путь?",
                f"Использовать предыдущий каталог?\n{last_dir}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            folder = last_dir
        else:
            folder = QFileDialog.getExistingDirectory(
                self, "Выберите папку с изображениями"
            )
            if folder:
                with open(LAST_DIR_FILE, "w") as f:
                    f.write(folder)

        if not folder:
            QMessageBox.warning(self, "Ошибка", "Папка не выбрана!")
            sys.exit()

        self.image_files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(("png", "jpg", "jpeg"))
        ]

        random.shuffle(self.image_files)

    def show_next_image(self):
        if self.current_index >= len(self.image_files):
            QMessageBox.information(self, "Готово", "Все изображения размечены!")
            self.close()
            return

        img_path = self.image_files[self.current_index]
        pixmap = QPixmap(img_path)
        self.image_label.setPixmap(
            pixmap.scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio)
        )

    def annotate(self, label):
        img_path = self.image_files[self.current_index]
        self.annotations[os.path.basename(img_path)] = label
        self.processed_count += 1
        self.current_index += 1
        self.save_progress()
        self.update_stats()
        self.show_next_image()

    def skip_image(self):
        img_path = self.image_files[self.current_index]
        self.skipped.add(os.path.basename(img_path))
        self.current_index += 1
        self.save_progress()
        self.show_next_image()

    def save_progress(self):
        with open(SAVE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            for k, v in self.annotations.items():
                writer.writerow([k, v])

        with open(SKIP_FILE, "w") as f:
            for img in self.skipped:
                f.write(img + "\n")

    def loadProgress(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                reader = csv.reader(f)
                self.annotations = {rows[0]: rows[1] for rows in reader}

        if os.path.exists(SKIP_FILE):
            with open(SKIP_FILE, "r") as f:
                self.skipped = set(f.read().splitlines())

        self.image_files = [
            f for f in self.image_files if os.path.basename(f) not in self.annotations
        ]
        self.current_index = 0

    def update_stats(self):
        class_counts = {lbl: 0 for lbl in LABELS}
        for label in self.annotations.values():
            if label in class_counts:
                class_counts[label] += 1

        self.ax.clear()
        self.ax.bar(class_counts.keys(), class_counts.values())
        self.ax.set_title("Классы")
        self.ax.set_xlim(-0.5, len(class_counts) - 0.5)
        self.figure.subplots_adjust(left=0.25)  # Дополнительный отступ слева
        self.canvas.draw()

        elapsed_time = (time.time() - self.start_time) / 60
        speed = self.processed_count / elapsed_time if elapsed_time > 0 else 0
        self.stats_label.setText(
            f"Размечено: {len(self.annotations)} | Пропущено: {len(self.skipped)} | Скорость: {speed:.2f} шт/мин"
        )

    def show_hotkey_config(self):
        dialog = HotkeyConfigDialog(self)
        dialog.exec()

    def apply_hotkey_config(self, config):
        # Update button visibility
        for label, btn in zip(LABELS, self.btns):
            btn.setVisible(config["buttons"].get(label, {}).get("visible", True))
        self.skip_btn.setVisible(config["buttons"].get("skip", {}).get("visible", True))

        # Setup global hotkeys if needed
        if config["global_hotkeys"]:
            if self.hotkey_listener:
                self.hotkey_listener.stop()

            self.hotkey_listener = keyboard.Listener(on_press=self.on_global_hotkey)
            self.hotkey_listener.start()
        elif self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None

    def load_hotkey_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.apply_hotkey_config(config)

    def keyPressEvent(self, event):
        if not self.hotkey_listener:  # Only handle local hotkeys if global are disabled
            key_text = QKeySequence(event.key()).toString()
            self.handle_hotkey(key_text)

    def on_global_hotkey(self, key):
        try:
            key_text = key.char
        except AttributeError:
            key_text = str(key)
        self.handle_hotkey(key_text)

    def handle_hotkey(self, key_text):
        # Load current config
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        # Check for label hotkeys
        for label in LABELS:
            if config["buttons"].get(label, {}).get("hotkey") == f"Клавиша: {key_text}":
                self.annotate(label)
                return

        # Check skip hotkey
        if config["buttons"].get("skip", {}).get("hotkey") == f"Клавиша: {key_text}":
            self.skip_image()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageLabelingApp()
    window.show()
    sys.exit(app.exec())
