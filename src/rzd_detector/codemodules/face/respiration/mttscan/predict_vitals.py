from .model import MTTS_CAN
import matplotlib.pyplot as plt
from scipy.signal import butter
from .inference_preprocess import preprocess_raw_video, detrend

import numpy as np
import scipy.io
import sys
import argparse

sys.path.append("../")


def predict_vitals(video_path, sampling_rate=30, batch_size=100, show_plot=False):
    '''Прогнозирует частоту дыхания и пульс по видео.
    
    Args:
        video_path (str): Путь к видеофайлу, на основе которого будут прогнозироваться показатели.
        sampling_rate (int, optional): Частота, с которой кадры извлекаются из видео (по умолчанию 30 кадров в секунду).
        batch_size (int, optional): Количество образцов, обработанных до обновления модели (по умолчанию 100).
        show_plot (bool, optional): Показ графиков и изображений (по умолчанию включено).
    Returns:
        tu: список спрогнозированных значений дыхания(1) и пульса(2), а также длина видео, из которого получены эти значения.
    '''
    img_rows = 36
    img_cols = 36
    frame_depth = 10
    model_checkpoint = "./mtts_can.hdf5"
    fs = sampling_rate
    # print("1111")
    print(video_path)
    dXsub, video_duration = preprocess_raw_video(video_path, dim=36)
    # print("dXsub shape", dXsub.shape)

    dXsub_len = (dXsub.shape[0] // frame_depth) * frame_depth
    dXsub = dXsub[:dXsub_len, :, :, :]

    model = MTTS_CAN(frame_depth, 32, 64, (img_rows, img_cols, 3))
    model.load_weights(model_checkpoint)

    yptest = model.predict(
        (dXsub[:, :, :, :3], dXsub[:, :, :, -3:]), batch_size=batch_size, verbose=1
    )

    pulse_pred = yptest[0]
    pulse_pred = detrend(np.cumsum(pulse_pred), 100)
    [b_pulse, a_pulse] = butter(1, [0.75 / fs * 2, 2.5 / fs * 2], btype="bandpass")
    pulse_pred = scipy.signal.filtfilt(b_pulse, a_pulse, np.double(pulse_pred))

    resp_pred = yptest[1]
    resp_pred = detrend(np.cumsum(resp_pred), 100)
    [b_resp, a_resp] = butter(1, [0.08 / fs * 2, 0.5 / fs * 2], btype="bandpass")
    resp_pred = scipy.signal.filtfilt(b_resp, a_resp, np.double(resp_pred))

    # ---------- Plot ----------------
    if show_plot:
        plt.subplot(211)
        plt.plot(pulse_pred)
        plt.title("Pulse Prediction")
        plt.subplot(212)
        plt.plot(resp_pred)
        plt.title("Resp Prediction")
        plt.show()
        plt.close()
    
    return pulse_pred, resp_pred, video_duration


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--video_path", type=str, help="processed video path")
    parser.add_argument(
        "--sampling_rate", type=int, default=30, help="sampling rate of your video"
    )
    parser.add_argument(
        "--batch_size", type=int, default=100, help="batch size (multiplier of 10)"
    )
    args = parser.parse_args()

    predict_vitals(args)
