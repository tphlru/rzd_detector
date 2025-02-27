from rzd_detector.codemodules.face.emotions.main_em import get_emotion
import logging
import json
logger = logging.getLogger(__name__)
{0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy',
                4: 'sad', 5: 'surprise', 6: 'neutral'}
emotions_list = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
def set_emo(emotion: str, emo_score: dict):
    print("Emo----------")
    with open("Scripts/table_values.json", mode="r") as jf:
        dt = dict(json.load(jf))
    dt[emotion+"_emo"] = {}
    dt[emotion+"_emo"]["category"] = "emotional"
    dt[emotion+"_emo"]["sublevel"] = emotion
    keyys = list(list(x.keys())[0] for x in emo_score)
    emo_score = {list(x.items())[0][0] : list(x.items())[0][1] for x in emo_score}
    if emotion in keyys:
        dt[emotion+"_emo"]["score"] = int(emo_score[emotion]*100)
    else:
         dt[emotion+"_emo"]["score"] = 0
    with open("Scripts/table_values.json", mode="w") as jf:
                json.dump(dt, jf)
def get_emo(video_path):
    try:
        emo_score = get_emotion(video_path)
        for i in emotions_list:
            set_emo(i, emo_score)
    except Exception as e:
        logger.error(e)
get_emo("upload/10.mp4")