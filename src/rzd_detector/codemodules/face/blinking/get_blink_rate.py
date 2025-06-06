import numpy as np
import mediapipe as mp
import cv2
from rzd_detector.common.utils import get_plot_tops_n_times as get_maxs
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode



options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=VisionRunningMode.VIDEO,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    output_face_blendshapes=True,
)

blink_scores_left = []
blink_scores_right = []

def get_blinking_count(video_path: str, plot=False) -> float:
    '''Вычиляет частоту моргания раз/минуту.
    Args:
        video_path (str): Путь к видео, по которому будет вычисляться частота.
    Returns:
        float: Количество морганий в минуту.
    '''
    video = cv2.VideoCapture(video_path)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/video.get(cv2.CAP_PROP_FPS)
    with FaceLandmarker.create_from_options(options) as landmarker:
        for i in range(frame_count):
            _, frame = video.read()
            frame_timestamp_ms = int(video.get(cv2.CAP_PROP_POS_MSEC))
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            face_landmarker_result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

            blendshapes = face_landmarker_result.face_blendshapes[0]

            blink_scores_left.append(blendshapes[9].score)
            blink_scores_right.append(blendshapes[10].score)
            blink_scores = [(x + y) / 2 for x, y in zip(blink_scores_left, blink_scores_right)]
            blink_scores = np.array(blink_scores)
            # midpoints, tnums, tops_values = get_maxs(blink_scores, iter_for_maxs)
            peaks, _ = find_peaks(blink_scores, distance=100)
            peaks = np.array(peaks)
            if plot:
                plt.figure()
                xs = list(range(len(blink_scores)))
                plt.plot(xs, blink_scores)
                plt.plot(peaks, blink_scores[peaks], "go") 
                plt.savefig("blink.png")
                plt.close()
    return len(peaks)*60/duration

