import cv2
from rzd_detector.codemoduls.stream.webrtc_receiver import WHEPClient, get_hsd_camera_url

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.