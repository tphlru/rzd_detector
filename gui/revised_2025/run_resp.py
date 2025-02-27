from rzd_detector.codemodules.face.respiration.get_resp import get_resp
import json
import logging
logger = logging.getLogger(__name__)

def resp(video_path):
    print("Resp----------")
    try:
        resp_rate, resp_score = get_resp(video_path=video_path)
        with open("Scripts/table_values.json", mode="r") as jf:
            dt = dict(json.load(jf))
        dt["resp"] = {}
        dt["resp"]["category"] = "physical"
        dt["resp"]["sublevel"] = "breathing"
        dt["resp"]["score"] = resp_score
        with open("Scripts/table_values.json", mode="w") as jf:
            json.dump(dt, jf)
    except Exception as e:
        logger.error(e)

resp("upload/10.mp4")