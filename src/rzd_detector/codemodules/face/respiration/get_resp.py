from respiration.mttscan.predict_vitals import predict_vitals
from common.utils import get_plot_tops_n_times
import numpy as np

def get_resp(iter_for_maxs: int, maxs_treshold: int) -> tuple:
    '''Объеденяет весь модуль.
    Args:
        iter_for_maxs (int): Число итераций, при поиске верхушек графика дыхания (вздохов).
        maxs_treshold (int): Порог количества пиков (вздохов) ниже, которого к значениям применятеся экстраполяция.
    Returns:
        tu: частота дыхания, оценка дыхания.
    '''
    predicted_resp, predicted_pulse, duration = predict_vitals(show_plot=False)
    mids, ids_tops, vals_tops = get_plot_tops_n_times(predicted_resp, iter_for_maxs)
    if len(ids_tops) < maxs_treshold:
        #экстрополируем
        resp_rate = len(ids_tops)*60/duration # подставляем новые значения пиков и новое время(надо подумать как его вычислять, это вроде как проблема), а потом вычисляем новое значение частоты дыхания
    resp_rate = len(ids_tops)*60/duration
    points = 0 
    if 12 < resp_rate < 20:
        points += 1
    elif resp_rate < 8 or resp_rate > 25:
        points -= 1
    if max(vals_tops) / np.mean(vals_tops) > 1.5:
        points -= 1
    
    return resp_rate, points