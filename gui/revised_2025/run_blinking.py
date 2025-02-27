from rzd_detector.codemodules.face.blinking.rating import get_score
import json
import logging
logger = logging.getLogger(__name__)

def blink(video_path):
    print("Blink----------")
    try:
        blink_rate, blink_scores = get_score(video_path=video_path)
        with open("Scripts/table_values.json", mode="r") as jf:
            dt = dict(json.load(jf))
        dt["blink"] = {}
        dt["blink"]["category"] = "physical"
        dt["blink"]["sublevel"] = "blinking"
        dt["blink"]["score"] = blink_scores
        with open("Scripts/table_values.json", mode="w") as jf:
            json.dump(dt, jf)
    except Exception as e:
        logger.error(e)

blink("upload/10.mp4")