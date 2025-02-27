from rzd_detector.codemodules.face.pulse import get_bpm_with_pbv, process_pulse_info, evaluate_pulse_results
import json
import logging
logger = logging.getLogger(__name__)

def pulse(cuda, video_path):
    try:
        bvp, times, bpm = get_bpm_with_pbv(cuda=cuda, videoFileName=video_path)
        base_mean, trend, high_med, mids, tvals = process_pulse_info(bpm, show_plot=False, plot_path="pulse.png")
        pulse_score = evaluate_pulse_results(base_mean=base_mean, trend=trend, high_med=high_med, midpoints=mids, tops_values=tvals)
        with open("Scripts/table_values.json", mode="r") as jf:
            dt = dict(json.load(jf))
        dt["pulse"] = {}
        dt["pulse"]["category"] = "physical"
        dt["pulse"]["sublevel"] = "pulse"
        dt["pulse"]["score"] = pulse_score
        with open("Scripts/table_values.json", mode="w") as jf:
            json.dump(dt, jf)
    except Exception as e:
        logger.error(e)

pulse(False, "upload/10.mp4")