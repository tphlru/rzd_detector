"""Сюда можно писать основной кастомный код. Он будет запускаться после обновления."""
import time


def post_start():
	print(">>> post_start script is running")
	while True:
		time.sleep(5)
		print("Hello Pi!")
