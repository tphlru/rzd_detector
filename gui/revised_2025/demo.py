import random
import time
import socketio
import logging
import cv2

import contextlib, os, logging
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO
import numpy as np
import asyncio
from queue import Queue
import threading

# from run_moduls import run as run_moduls
import eventlet
import eventlet.wsgi
from rzd_detector.codemodules.stream.crop_face import crop_face
import multiprocessing as mp
from multiprocessing import shared_memory
from rzd_detector.codemodules.stream.webrtc_receiver import WHEPClient, get_hsd_camera_url
logging.basicConfig(level=logging.INFO)
sio = socketio.Client()

FRAME_SHAPE = (1080, 1920, 3)
FRAME_DTYPE = np.uint8
HSD_IP = "192.168.0.102"

frame_queue = asyncio.Queue(maxsize=30)  # Асинхронная очередь для хранения кадров
frame_var = None

shm = shared_memory.SharedMemory(create=True, size=np.prod(FRAME_SHAPE) * np.dtype(FRAME_DTYPE).itemsize)
frame_array = np.ndarray(FRAME_SHAPE, dtype=FRAME_DTYPE, buffer=shm.buf)
predicts_data = shared_memory.SharedMemory(create=True, size = 4 * np.dtype(np.uint8).itemsize)
pred = np.ndarray((4,), dtype=np.uint8, buffer=predicts_data.buf)
new_frame_event = mp.Event()
new_predict_event = mp.Event()

update_data = {
    "category": "physical",
    "sublevel": "pulse",
    "score": pred[1]
}

def translate_score():
    while True:
        new_predict_event.wait()
        new_predict_event.clear()
        predict = pred
        update_data = {
            "category": "physical",
            "sublevel": "pulse",
            "score": predict[1]
        }
        sio.emit("update_criteria", update_data)

def get_predict():
    while True:
        new_frame_event.wait()  # Ждем новый кадр
        new_frame_event.clear()
        frame = frame_array
        # pulse, resp, blink, emotions = run_moduls(False, frame)
        pred[0] = 1
        pred[1] = 2
        pred[2] = 3
        pred[3] = 4
        print(pred)
        new_predict_event.set()

async def generate_stream():
    """Асинхронная функция для генерации потока видео"""
    new_frame_event.set()
    # client = WHEPClient(get_hsd_camera_url(HSD_IP))
    # await client.connect()
    # while True:
    #     frame = await client.get_raw_frame()
    #     frame = crop_face(frame)
    #     global frame_array
    #     frame_array[:] = np.array(dtype=FRAME_DTYPE)
    #     new_frame_event.set()
    #     await asyncio.sleep(0.03)  # Небольшая задержка для уменьшения нагрузки


# @socketio.on('start_video')
# def start_video():
#     print("aa")
#     socketio.start_background_task(generate_stream)

def main():
    generate = mp.Process(target=asyncio.run(generate_stream()))
    generate.start()
    predict = mp.Process(target=get_predict)
    predict.start()

# def generate_random_scores():
#     categories = ["emotional", "physical", "seasonal", "subjective", "statistical"]
#     sublevels = {
#         "emotional": ["happiness", "stress", "anxiety"],
#         "physical": ["pulse", "breathing", "blinking"],
#     }

#     while True:
#         try:
#             # Update main categories
#             for category in categories:
#                 if category in sublevels:
#                     for sublevel in sublevels[category]:
#                         update_data = {
#                             "category": category,
#                             "sublevel": sublevel,
#                             "score": random.randint(0, 5),
#                         }
#                         sio.emit("update_criteria", update_data)
#                         time.sleep(1)
#                 else:
#                     update_data = {
#                         "category": category,
#                         "sublevel": None,
#                         "score": random.randint(0, 5),
#                     }
#                     sio.emit("update_criteria", update_data)
#                     time.sleep(1)

#             time.sleep(5)

#         except Exception as e:
#             logging.error(f"Error in demo: {e}")
#             time.sleep(5)


@sio.event
def connect():
    logging.info("Connected to server")
    # generate_random_scores()
    # get_predict()
    main()


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
