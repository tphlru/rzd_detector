import uuid
import toml
import time


# Функция для определения текущего устройства
def get_current_device(devices_toml="devices.toml"):
	devices = {}

	# Читаем файл toml и заполняем словарь устройств
	try:
		with open(devices_toml, "r") as f:
			devices = toml.load(f)
	except FileNotFoundError:
		print("Файл devices.toml не найден")
		
	# Получаем уникальный идентификатор устройства
	device_id = ''.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 48, 8)][::-1])
	print(devices)
	print("Уникальный идентификатор устройства:", device_id)
	return devices.get(device_id, None)


if __name__ == "__main__":
	print("Текущее устройство:", get_current_device())
	while True:
		time.sleep(1)
		print("Hello")
