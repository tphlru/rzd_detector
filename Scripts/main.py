# from rzd_detector.codemodules.face.pulse import get_bpm_with_pbv, process_pulse_info

# # import matplotlib.pyplot as plt


# bvps_win_m, timesES, bpmES = get_bpm_with_pbv("Scripts/test_files/pulse/high.mp4")
# process_pulse_info(bpmES, base_offset=10, show_plot=True, plot_path="example.png")

from rzd_detector.codemodules.behaviour.clothes import (
    is_dressed_for_weather,
    get_clothes,
    get_weather,
)
import cv2

image = cv2.imread("Scripts/test_files/clothes/test3.webp")
clothes = get_clothes(image, show=True, thresh=0.5)
API_KEY = "***"
temperature, season = get_weather(API_KEY, CITY="Yaroslavl", defaults=(10, "other"))
print("Clothes: ", clothes)
print("Temperature: ", temperature, "Season: ", season)
result = is_dressed_for_weather(clothes, temperature, season)
print("Result: ", result)
