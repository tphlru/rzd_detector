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

weights_score = {
    "pulse": 1,
    "resp": 1,
    "blink": 1,
    "emotion": 1
}
def set_param(param, value):
    with open("Scripts/table_values.json", mode="r") as jf:
        dt = dict(json.load(jf))
    dt[param] = value
    with open("Scripts/table_values.json", mode="w") as jf:
        json.dump(dt, jf)
def write_table(a, b, c):
    return {"category": a, "sublevel": b, "score": c}

def run(cuda: bool, video_path):
    set_param("status", "working")
    print("start")
    t = timeit.default_timer()
    try:
        bvp, times, bpm = get_bpm_with_pbv(cuda=cuda, videoFileName=video_path)
        base_mean, trend, high_med, mids, tvals = process_pulse_info(bpm, show_plot=False, plot_path = "pulse.png")
        pulse_score = evaluate_pulse_results(base_mean=base_mean, trend=trend, high_med=high_med, midpoints=mids, tops_values=tvals)
    except:
        set_param("status", "error")
    try:
        resp_rate, resp_score = get_resp(video_path=video_path, iter_for_maxs=8, maxs_treshold=3)
    except:
        set_param("status", "error")
    try:
        blink_rate, blink_scores = get_score(video_path=video_path, iter_for_maxs=5)
    except:
        set_param("status", "error")

    try:
        emotions = get_emotion(video_path)
        # emotion_score = 
    except:
        set_param("status", "error")
    print("finished", timeit.default_timer() - t)
    with open("/home/LaboRad/rzd_detector/Scripts/table_values.json", "w") as f:
        d = {
            "pulse":write_table("physical", "pulse", int(pulse_score)),
            "resp":write_table("physical", "breathing", int(resp_score) + 2),
            "blink":write_table("physical", "blinking", blink_scores)
        }
        json.dump(d, f)
    return pulse_score, resp_score, blink_rate, emotions
    # return blink_rate
if __name__ == "__main__":
    print(run(True, "Scripts/test_files/common/example1.mp4"))