from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import json

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == "/home/LaboRad/rzd_detector/Scripts/test_files/test.json":
            print("File changed!")

observer = Observer()
event_handler = FileChangeHandler()
observer.schedule(event_handler, "/home/LaboRad/rzd_detector/Scripts/test_files/test.json", recursive=False)
observer.start()

try:
    while True:
        time.sleep()
        print("sleep")
except KeyboardInterrupt:
    observer.stop()

observer.join()

def write_(a, b, c, path):
    d = {"category": a, "sublevel": b, "score": c}
    with open(path) as f:
        json.dump(d, f)
    return 