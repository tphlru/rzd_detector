# emotions - :(
# pulse - ✓
# respiration - ✓ (нет экстраполяции)
# blinking - ✓
# voice - 
from rzd_detector.codemodules.face.pulse import get_bpm_with_pbv, process_pulse_info, evaluate_pulse_results
from rzd_detector.codemodules.face.respiration import get_resp
from rzd_detector.codemodules.face.blinking import get_score as get_blink
def main(cuda: bool, video_path):
    bvp, times, bpm = get_bpm_with_pbv(videoFileName=video_path, cuda=cuda)
    base_mean, trend, high_med, mids, tvals = process_pulse_info(bvp, show_plot=False)
    pulse_score = evaluate_pulse_results(base_mean=base_mean, trend=trend, high_med=high_med, midpoints=mids, tops_values=tvals)

    resp_rate, resp_score = get_resp(video_path=video_path, iter_for_maxs=8, maxs_treshold=3) # значения на рандом

    blink_score = get_blink(video_path=video_path)

