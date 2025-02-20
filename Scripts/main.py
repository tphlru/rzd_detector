# emotions - :(
# pulse
# respiration
# voice
from rzd_detector.codemodules.face.pulse import get_bpm_with_pbv, process_pulse_info, evaluate_pulse_results
from rzd_detector.codemodules.face.respiration import 
def main(cuda: bool):
    bvp, times, bpm = get_bpm_with_pbv(videoFileName="Scripts\test_files\common\example1.mp4", cuda=cuda)
    base_mean, trend, high_med, mids, tvals = process_pulse_info(bvp, show_plot=False)
    pulse_points = evaluate_pulse_results(base_mean=base_mean, trend=trend, high_med=high_med, midpoints=mids, tops_values=tvals)

