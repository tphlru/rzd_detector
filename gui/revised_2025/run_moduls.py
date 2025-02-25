# emotions - :(
# pulse - ✓
# respiration - ✓ (нет экстраполяции)
# blinking - ✓
# voice - 
from rzd_detector.codemodules.face.pulse import get_bpm_with_pbv, process_pulse_info, evaluate_pulse_results
from rzd_detector.codemodules.face.respiration.get_resp import get_resp
from rzd_detector.codemodules.face.blinking.get_blink_rate import get_blinking_count as get_blink
from rzd_detector.codemodules.face.emotions.main_em import get_emotion
import timeit

def run(cuda: bool, video_path):
    print("start")
    t = timeit.default_timer()
    bvp, times, bpm = get_bpm_with_pbv(cuda=cuda, videoFileName=video_path)
    base_mean, trend, high_med, mids, tvals = process_pulse_info(bpm, show_plot=False, plot_path = "pulse.png")
    pulse_score = evaluate_pulse_results(base_mean=base_mean, trend=trend, high_med=high_med, midpoints=mids, tops_values=tvals)

    resp_rate, resp_score = get_resp(video_path=video_path, iter_for_maxs=8, maxs_treshold=3)

    blink_rate = get_blink(video_path=video_path, iter_for_maxs=5)

    emotions = get_emotion(video_path)
    print("finished", timeit.default_timer() - t)
    return pulse_score, resp_score, blink_rate, emotions
    # return blink_rate
if __name__ == "__main__":
    print(run(True, "Scripts/test_files/pulse/high.mp4"))