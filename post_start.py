"""Сюда можно писать основной кастомный код. Он будет запускаться после обновления."""
# import time

import io
import logging
import socketserver
from http import server
from threading import Condition
import libcamera
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
	def __init__(self):
		self.frame = None
		self.condition = Condition()

	def write(self, buf):
		with self.condition:
			self.frame = buf
			self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			self.send_response(301)
			self.send_header('Location', '/index.html')
			self.end_headers()
		elif self.path == '/index.html':
			content = PAGE.encode('utf-8')
			self.send_response(200)
			self._extracted_from_do_GET_9('text/html', content)
		elif self.path == '/stream.mjpg':
			self._extracted_from_do_GET_14()
		else:
			self.send_error(404)
			self.end_headers()

	# TODO Rename this here and in `do_GET`
	def _extracted_from_do_GET_14(self):
		global output
		self.send_response(200)
		self.send_header('Age', 0)
		self.send_header('Cache-Control', 'no-cache, private')
		self.send_header('Pragma', 'no-cache')
		self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
		self.end_headers()
		try:
			while True:
				with output.condition:
					output.condition.wait()
					frame = output.frame
				self.wfile.write(b'--FRAME\r\n')
				self._extracted_from_do_GET_9('image/jpeg', frame)
				self.wfile.write(b'\r\n')
		except Exception as e:
			logging.warning(
				'Removed streaming client %s: %s',
				self.client_address, str(e))

	def _extracted_from_do_GET_9(self, arg0, arg1):
		self.send_header('Content-Type', arg0)
		self.send_header('Content-Length', len(arg1))
		self.end_headers()
		self.wfile.write(arg1)


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
	allow_reuse_address = True
	daemon_threads = True


def post_start():
	picam2 = Picamera2()
	config = picam2.create_video_configuration(main={"size": (1280, 720)})
	config["transform"] = libcamera.Transform(hflip=1, vflip=1)
	picam2.configure(config)
	global output
	output = StreamingOutput()
	picam2.start_recording(JpegEncoder(), FileOutput(output))

	try:
		address = ('', 8000)
		server = StreamingServer(address, StreamingHandler)
		server.serve_forever()
	finally:
		picam2.stop_recording()
	# print(">>> post_start script is running")
	# while True:
	# 	time.sleep(5)
	# 	print("Hello Pi!")
