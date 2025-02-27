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

maindict = dict()#{
#     "category1": {
#         "score": 10,
#         "max_score": 20,
#         "sublevels": {
#             "sub1": {
#                 "score": 5,
#                 "max_score": 10
#             },
#             "sub2": {
#                 "score": 7,
#                 "max_score": 15
#             }
#         }
#     },
#     "category2": {
#         "score": 15,
#         "max_score": 30
#     }
# }

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == "Scripts/table_values.json":
            with open("Scripts/table_values.json", "r") as data:
                try:
                    maindict = json.load(data)
                except json.decoder.JSONDecodeError:
                    print("Incorrect format")
            # print(maindict)
            # sio.emit("update_criteria", maindict["pulse"])# TODO: нужно отправлять всеразделы файла json а н только pulse
            dict_values = list(x for x in maindict.values() if type(x) == dict)
            for i in dict_values:
                sio.emit("update_criteria", i)
                print("update_criteria", i)

@sio.event
def connect():
    logging.info("Connected to server")
    observer = Observer()
    event_handler = FileChangeHandler()
    observer.schedule(event_handler, "Scripts/table_values.json", recursive=False)
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