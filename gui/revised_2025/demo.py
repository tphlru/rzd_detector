import time
import socketio
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import numpy as np
import json

logging.basicConfig(level=logging.INFO)
sio = socketio.Client()


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == "/home/LaboRad/rzd_detector/Scripts/table_values.json":
            with open("/home/LaboRad/rzd_detector/Scripts/table_values.json", "r") as data:
                update_data = json.load(data)
            for x in update_data.values():
                sio.emit("update_criteria", x)

FRAME_SHAPE = (1080, 1920, 3)
FRAME_DTYPE = np.uint8
HSD_IP = "192.168.0.102"
frame_var = None


update_data = {}

@sio.event
def connect():
    logging.info("Connected to server")
    with open("/home/LaboRad/rzd_detector/Scripts/table_values.json", "r") as data:
        update_data = dict(json.load(data))
    for x in update_data.values():
        sio.emit("update_criteria", x)
    observer = Observer()
    event_handler = FileChangeHandler()
    observer.schedule(event_handler, "/home/LaboRad/rzd_detector/Scripts/table_values.json", recursive=False)
    observer.start()


@sio.event
def disconnect():
    logging.info("Disconnected from server")

if __name__ == "__main__":
    while True:
        try:
            sio.connect("http://localhost:5000")
            sio.wait()
        except Exception as e:
            logging.error(f"Connection error: {e}")
            time.sleep(5)