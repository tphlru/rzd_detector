# from rzd_detector.codemodules.face.respiration import get_resp
# import matplotlib.pyplot as plt


# bvps_win_m, timesES, bpmES = get_bpm_with_pbv("/home/timur/Video/tetr/gesha_otvra.mp4")
# process_pulse_info(bpmES, base_offset=10, show_plot=True, plot_path="disgust.png")

# # from rzd_detector.codemodules.behaviour.clothes import (
# #     is_dressed_for_weather,
# #     get_clothes,
# #     get_weather,
# # )
# # import cv2

# # image = cv2.imread("Scripts/test_files/clothes/test3.webp")
# # clothes = get_clothes(image, show=True, thresh=0.5)
# # API_KEY = "***"
# # temperature, season = get_weather(API_KEY, CITY="Yaroslavl", defaults=(10, "other"))
# # print("Clothes: ", clothes)
# # print("Temperature: ", temperature, "Season: ", season)
# # result = is_dressed_for_weather(clothes, temperature, season)
# # print("Result: ", result)

import time
from pynput import keyboard


def main():
    print("Программа отслеживает нажатия клавиши 'v' в течение 35 секунд.")
    print("Нажимайте 'v' и ждите завершения.")

    start_time = time.time()
    duration = 35  # Продолжительность в секундах
    pressed_times = []

    def on_press(key):
        try:
            if key.char == "v":
                # Запоминаем временную метку относительно начала работы программы
                pressed_times.append(time.time() - start_time)
        except AttributeError:
            pass

    # Создаем слушателя клавиатуры
    with keyboard.Listener(on_press=on_press) as listener:
        while time.time() - start_time < duration:
            time.sleep(0.1)  # Минимальная задержка для снижения нагрузки на процессор
        listener.stop()

    print("Время завершено.")
    print("Временные метки нажатий:")
    print(pressed_times)


if __name__ == "__main__":
    main()
