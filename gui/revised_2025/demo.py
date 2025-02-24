import random
import time
import socketio
import logging

logging.basicConfig(level=logging.INFO)
sio = socketio.Client()


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


@sio.event
def connect():
    logging.info("Connected to server")
    generate_random_scores()


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
