import time
import socketio
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import numpy as np
import json

import random

logging.basicConfig(level=logging.INFO)
sio = socketio.Client()


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == "/home/LaboRad/rzd_detector/Scripts/table_values.json":
            with open("/home/LaboRad/rzd_detector/Scripts/table_values.json", "r") as data:
                update_data = json.load(data)
            print(update_data)
            sio.emit("update_criteria", update_data['1'])
            sio.emit("update_criteria", update_data['2'])
            sio.emit("update_criteria", update_data['3'])

FRAME_SHAPE = (1080, 1920, 3)
FRAME_DTYPE = np.uint8
HSD_IP = "192.168.0.102"
frame_var = None



def generate_random_scores():
    categories = ["emotional", "physical", "seasonal", "subjective", "statistical"]
    sublevels = {
        "emotional": ["happiness", "stress", "anxiety"],
        "physical": ["pulse", "breathing", "blinking"],
    }

    while True:
        try:
            # Update main categories
            for category in categories:
                if category in sublevels:
                    for sublevel in sublevels[category]:
                        update_data = {
                            "category": category,
                            "sublevel": sublevel,
                            "score": random.randint(0, 5),
                        }
                        sio.emit("update_criteria", update_data)
                        time.sleep(1)
                else:
                    update_data = {
                        "category": category,
                        "sublevel": None,
                        "score": random.randint(0, 5),
                    }
                    sio.emit("update_criteria", update_data)
                    time.sleep(1)

            time.sleep(5)

        except Exception as e:
            logging.error(f"Error in demo: {e}")
            time.sleep(5)

update_data = {}

@sio.event
def connect():
    logging.info("Connected to server")
    
    # with open("/home/LaboRad/rzd_detector/Scripts/table_values.json", "r") as data:
    #     update_data = json.load(data)
    # print(update_data)
    # sio.emit("update_criteria", update_data)
    # observer = Observer()
    # event_handler = FileChangeHandler()
    # observer.schedule(event_handler, "/home/LaboRad/rzd_detector/Scripts/table_values.json", recursive=False)
    # observer.start()


@sio.event
def disconnect():
    logging.info("Disconnected from server")
    generate_random_scores()

if __name__ == "__main__":
    while True:
        try:
            sio.connect("http://localhost:5000")
            sio.wait()
        except Exception as e:
            logging.error(f"Connection error: {e}")
            time.sleep(5)