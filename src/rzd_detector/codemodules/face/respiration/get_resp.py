from respiration.mttscan.predict_vitals import predict_vitals
from common.utils import get_plot_tops_n_times
def get_resp(iter_for_maxs: int):
    '''Объеденяет весь модуль.
    Args:
        iter_for_maxs (int): Число итераций, при поиске верхушек графика дыхания (вздохов).
    Returns:
        tu: частота дыхания, оценка дыхания.
    '''
    predicted_resp, predicted_pulse = predict_vitals(video_path="Scripts/test_files/common/example1.mp4", show_plot=False)
    mids, ids_tops, vals_tops = get_plot_tops_n_times(predicted_resp, iter_for_maxs)
    resp_rate = len(ids_tops)
    
    return resp_rate, points