"""Сюда можно писать основной кастомный код. Он будет запускаться после обновления."""
# import time

from flask import Flask, Response
from picamera2 import Picamera2
import cv2

# Flask app setup
app = Flask(__name__)

# Camera setup
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(camera_config)
picam2.start()


def generate_frames():
	"""Generator for providing live frames."""
	while True:
		frame = picam2.capture_array()
		# Convert RGB888 to JPEG format
		_, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
		frame = buffer.tobytes()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
	"""Video feed route."""
	return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
	"""Landing page."""
	return '''
	<html>
		<head><title>Raspberry Pi Camera</title></head>
		<body>
			<h1>Raspberry Pi Live Camera Feed</h1>
			<img src="/video_feed" width="640" height="480">
		</body>
	</html>
	'''


def post_start():
	app.run(host='0.0.0.0', port=5000, debug=False)
	# print(">>> post_start script is running")
	# while True:
	# 	time.sleep(5)
	# 	print("Hello Pi!")
