from rzd_detector.codemodules.face.emotions.main_em import get_emotion
import logging
import json
logger = logging.getLogger(__name__)

def get_emo(video_path):
    try:
        emo_score = get_emotion(video_path)
        print(emo_score)
        with open("Scripts/table_values.json", mode="r") as jf:
            dt = dict(json.load(jf))
            dt["happy_emo"] = {}
            dt["happy_emo"]["category"] = "emotional"
            dt["happy_emo"]["sublevel"] = "happiness"
            dt["happy_emo"]["score"] = 1
            dt["stress_emo"] = {}
            dt["stress_emo"]["category"] = "emotional"
            dt["stress_emo"]["sublevel"] = "stress"
            dt["stress_emo"]["score"] = 1
            dt["anxiety_emo"] = {}
            dt["anxiety_emo"]["category"] = "emotional"
            dt["anxiety_emo"]["sublevel"] = "anxiety"
            dt["anxiety_emo"]["score"] = 1
            with open("Scripts/table_values.json", mode="w") as jf:
                json.dump(dt, jf)
    except Exception as e:
        logger.error(e)
get_emo("upload/10.mp4")