from .mttscan.predict_vitals import predict_vitals
from rzd_detector.common.utils import get_plot_tops_n_times, get_plot_tops_adaptive
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def get_resp(video_path) -> tuple:
    '''Объеденяет весь модуль.
    Args:
        iter_for_maxs (int): Число итераций, при поиске верхушек графика дыхания (вздохов).
        maxs_treshold (int): Порог количества пиков (вздохов) ниже, которого к значениям применятеся экстраполяция.
    Returns:
        tu: частота дыхания, оценка дыхания.
    '''
    predicted_resp, predicted_pulse, duration = predict_vitals(video_path, show_plot=False)
    # print("jjjj")
    # print("duration", duration)
    # mids, ids_tops, vals_tops = get_plot_tops_adaptive(predicted_resp, iter_for_maxs)
    # ids_tops = np.array(ids_tops)
    # vals_tops = np.array(vals_tops)

    plt.figure()  # Создаём новую фигуру
    peaks_max, _ = find_peaks(predicted_resp, distance=8)
    xs = np.array([x for x in range(len(predicted_resp))])
    predicted_resp = np.array(predicted_resp)
    ii=np.array(predicted_resp[peaks_max])
    peaks2, _ = find_peaks(ii, distance=8)
    plt.plot(xs, predicted_resp)
    plt.plot(xs[peaks2], ii[peaks2], "go") 
    print(len(peaks2))
    plt.savefig("respiration.png")
    plt.close()
    # print("ids_tops", ids_tops)
    # if len(ids_tops) < maxs_treshold:
    #     #экстрополируем
    #     resp_rate = len(ids_tops)*60/duration # подставляем новые значения пиков и новое время(надо подумать как его вычислять, это вроде как проблема), а потом вычисляем новое значение частоты дыхания
    # resp_rate = len(ids_tops)*60/duration
    resp_rate = (len(peaks_max)) / duration * 60
    points = 0
    if 12 < resp_rate < 20:
        points += 1
    elif resp_rate < 8 or resp_rate > 25:
        points -= 1
    if max(predicted_resp) / np.mean(predicted_resp) > 1.5:
        points -= 1
    
    return resp_rate, points