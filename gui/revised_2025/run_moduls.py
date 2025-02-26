# emotions - :(
# pulse - ✓
# respiration - ✓ (нет экстраполяции)
# blinking - ✓
# voice - 
from rzd_detector.codemodules.face.pulse import get_bpm_with_pbv, process_pulse_info, evaluate_pulse_results
from rzd_detector.codemodules.face.respiration.get_resp import get_resp
from rzd_detector.codemodules.face.blinking.rating import get_score
from rzd_detector.codemodules.face.emotions.main_em import get_emotion
import timeit
import json
from write_video import w as write
import asyncio
from multiprocessing import Process, Event
from events import start, stop, pause
from threading import Thread, Lock
import cv2
results = {}
lock = Lock()


def write_table(a, b, c):
    return {"category": a, "sublevel": b, "score": c}

def pulse(cuda, video_path):
    bvp, times, bpm = get_bpm_with_pbv(cuda=cuda, videoFileName=video_path)
    base_mean, trend, high_med, mids, tvals = process_pulse_info(bpm, show_plot=False, plot_path="pulse.png")
    pulse_score = evaluate_pulse_results(base_mean=base_mean, trend=trend, high_med=high_med, midpoints=mids, tops_values=tvals)
    with lock:
        results["pulse"] = pulse_score

def respiration(video_path, itrfmxs, mxtrshld):
    resp_rate, resp_score = get_resp(video_path=video_path, iter_for_maxs=itrfmxs, maxs_treshold=mxtrshld)
    with lock:
        results["resp"] = resp_score

def blinking(video_path, itrfmxs):
    blink_rate, blink_scores = get_score(video_path=video_path, iter_for_maxs=itrfmxs)
    with lock:
        results["blink"] = blink_scores

def run(cuda: bool, video_path, client):
    print("Предупреждение: Компания Meta признана экстримисткой организацией и запрещена в РФ. Используются только открытые, некоммерческие технологии.")
    start.wait()
    start.clear()
    t = timeit.default_timer()
    video, fps = asyncio.run(write(video_path, 10, True, None, None, client))
    for i in range(100):
        video = asyncio.run(write(video_path, 10, False, fps, video, client))
    video.release()
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_count*0.3))
    frame1 = video.read()
    video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_count * 0.6))
    frame2 = video.read()
    video.set(cv2.CAP_PROP_POS_FRAMES, int(frame_count * 0.9))
    frame3 = video.read()
    video.set(cv2.CAP_PROP_POS_FRAMES, 1)
    print("Запись завершена")
    thread_pulse = Thread(target=pulse, args=(cuda, video_path))
    thread_pulse.start()
    thread_pulse.append(thread_pulse)

    thread_resp = Thread(target=respiration, args=(video_path, 8, 3))
    thread_resp.start()
    thread_resp.append(thread_resp)

    thread_resp = Thread(target=blinking, args=(video_path, 8))
    thread_resp.start()
    thread_resp.append(thread_resp)

    emotions = get_emotion(video_path)
    print("Завершено, время предсказания значений:", timeit.default_timer() - t)
    with open("/home/LaboRad/rzd_detector/Scripts/table_values.json", "w") as f:
        d = {
            "pulse":write_table("physical", "pulse", results["pulse"]),
            "resp":write_table("physical", "breathing", results["resp"]),
            "blink":write_table("physical", "blinking", results["blink"])
        }
        json.dump(d, f)
    return emotions
    # return blink_rate
if __name__ == "__main__":
    print(run(True, "Scripts/test_files/pulse/high.mp4"))