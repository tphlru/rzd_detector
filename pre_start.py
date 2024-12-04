"""Этот скрипт выполняется перед запуском сервисов после обновления"""
import subprocess


def pre_start():
	print(">>> pre_start script is running")
	subprocess.run("/usr/bin/python3 -m pip install -r /home/timpy1/rpi/requirements.txt --break-system-packages".split())
