from rzd_detector.codemodules.face.emotions.main_em import get_emotion
import logging
logger = logging.getLogger(__name__)

def get_emo(video_path):
    try:
        get_emotion(video_path)
    except Exception as e:
        logger.error(e)

get_emo("upload/10.mp4")