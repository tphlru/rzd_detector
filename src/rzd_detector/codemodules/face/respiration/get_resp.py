from respiration.mttscan.predict_vitals import predict_vitals
from common.utils import get_plot_tops_n_times
def get_resp(iter_for_maxs: int, maxs_treshold: int):
    '''Объеденяет весь модуль.
    Args:
        iter_for_maxs (int): Число итераций, при поиске верхушек графика дыхания (вздохов).
        maxs_treshold (int): Порог ниже, которого к значениям применятеся экстраполяция.
    Returns:
        tu: частота дыхания, оценка дыхания.
    '''
    predicted_resp, predicted_pulse, duration = predict_vitals(video_path="Scripts/test_files/common/example1.mp4", show_plot=False)
    mids, ids_tops, vals_tops = get_plot_tops_n_times(predicted_resp, iter_for_maxs)
    if len(ids_tops) < maxs_treshold:
        #экстрополируем
        resp_rate = len(ids_tops)*60/duration # подставляем новые значения пиков и новое время(надо подумать как его вычислять, это вроде как проблема), а потом вычисляем новое значение частоты дыхания
    resp_rate = len(ids_tops)*60/duration
    points = 0 
    if 16 < resp_rate < 20:
        points += 1
    else:
        points -= 1
    return resp_rate, points