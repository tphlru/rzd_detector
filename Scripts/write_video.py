import cv2
from rzd_detector.codemoduls.stream.webrtc_receiver import WHEPClient, get_hsd_camera_url

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("output.mp4", fourcc, 30, (1080, 1920))
client = WHEPClient(get_hsd_camera_url("192.168.43.101"))
client.connect()
while True:
	try:
		frame = client.get_raw_frame()
		out.write(frame)
	except KeyboardIterrupt:
		print("Операция прервана пользователем")
client.close()
