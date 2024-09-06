# from rzd_detector.codemodules.face.pulse import get_bpm_with_pbv, process_pulse_info

# # import matplotlib.pyplot as plt


# bvps_win_m, timesES, bpmES = get_bpm_with_pbv("Scripts/test_files/pulse/high.mp4")

# print(bvps_win_m)

# process_pulse_info(bpmES, base_offset=10, show_plot=True, plot_path="example.png")

from rzd_detector.codemodules.behaviour.clothes.get_clothes import get_clothes
import cv2

image = cv2.imread("Scripts/test_files/clothes/test2.jpg")
get_clothes(image)
