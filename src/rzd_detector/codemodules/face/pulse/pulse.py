import logging
import os
import statistics
from random import choice
import matplotlib.pyplot as plt
import numpy as np
import cv2
import mediapipe as mp
from pyVHR.extraction.utils import *
from pyVHR.extraction.skin_extraction_methods import *
from pyVHR.extraction.sig_extraction_methods import *

from pyVHR.BPM.BPM import BPM_clustering
from pyVHR.BVP.BVP import RGB_sig_to_BVP
from pyVHR.BVP.filters import BPfilter, apply_filter
from pyVHR.BVP.methods import cpu_PBV
from pyVHR.extraction.sig_extraction_methods import SignalProcessingParams
from pyVHR.extraction.sig_processing import SignalProcessing
from pyVHR.extraction.skin_extraction_methods import (
    SkinExtractionConvexHull,
    SkinProcessingParams,
)
from pyVHR.extraction.utils import MotionAnalysis, sig_windowing

from .helpers_code import vhr_ldmks_list, get_largest_serially
from rzd_detector.common.utils import (
    add_offset_to_values,
    get_plot_tops_n_times,
    get_trend,
)
from stream import Filter


class NewSignalProcessing(SignalProcessing):
    def __init__(self, filter: Filter, client):
        # Common parameters #
        self.tot_frames = None
        self.visualize_skin_collection = []
        self.skin_extractor = SkinExtractionConvexHull()
        # Patches parameters #
        high_prio_ldmk_id, mid_prio_ldmk_id = get_magic_landmarks()
        self.ldmks = high_prio_ldmk_id + mid_prio_ldmk_id
        self.square = None
        self.rects = None
        self.visualize_skin = False
        self.visualize_landmarks = False
        self.visualize_landmarks_number = False
        self.visualize_patch = False
        self.font_size = 0.3
        self.font_color = (255, 0, 0, 255)
        self.visualize_skin_collection = []
        self.visualize_landmarks_collection = []
        self.filter = filter
        self.client = client

    def extract_patches(self, region_type, sig_extraction_method):
        """
        This method compute the RGB-mean signal using specific skin regions (patches).

        Args:
            videoFileName (str): video file name or path.
            region_type (str): patches types can be  "squares" or "rects".
            sig_extraction_method (str): RGB signal can be computed with "mean" or "median". We recommend to use mean.

        Returns: 
            float32 ndarray: RGB signal as ndarray with shape [num_frames, num_patches, rgb_channels].
        """
        if self.square is None and self.rects is None:
            print(
                "[ERROR] Use set_landmarks_squares or set_landmarkds_rects before calling this function!")
            return None
        if region_type != "squares" and region_type != "rects":
            print("[ERROR] Invalid landmarks region type!")
            return None
        if sig_extraction_method != "mean" and sig_extraction_method != "median":
            print("[ERROR] Invalid signal extraction method!")
            return None

        ldmks_regions = None
        if region_type == "squares":
            ldmks_regions = np.float32(self.square)
        elif region_type == "rects":
            ldmks_regions = np.float32(self.rects)

        sig_ext_met = None
        if sig_extraction_method == "mean":
            if region_type == "squares":
                sig_ext_met = landmarks_mean
            elif region_type == "rects":
                sig_ext_met = landmarks_mean_custom_rect
        elif sig_extraction_method == "median":
            if region_type == "squares":
                sig_ext_met = landmarks_median
            elif region_type == "rects":
                sig_ext_met = landmarks_median_custom_rect

        self.visualize_skin_collection = []
        self.visualize_landmarks_collection = []

        skin_ex = self.skin_extractor

        mp_drawing = mp.solutions.drawing_utils
        mp_face_mesh = mp.solutions.face_mesh
        PRESENCE_THRESHOLD = 0.5
        VISIBILITY_THRESHOLD = 0.5

        sig = []
        processed_frames_count = 0

        with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:
            while True:
                frame = filter.get_frame(self.client)
                if frame == None:
                    break
                image = frame.image
                # convert the BGR image to RGB.
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                processed_frames_count += 1
                width = image.shape[1]
                height = image.shape[0]
                # [landmarks, info], with info->x_center ,y_center, r, g, b
                ldmks = np.zeros((468, 5), dtype=np.float32)
                ldmks[:, 0] = -1.0
                ldmks[:, 1] = -1.0
                magic_ldmks = []
                ### face landmarks ###
                results = face_mesh.process(image)
                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]
                    landmarks = [l for l in face_landmarks.landmark]
                    for idx in range(len(landmarks)):
                        landmark = landmarks[idx]
                        if not ((landmark.HasField('visibility') and landmark.visibility < VISIBILITY_THRESHOLD)
                                or (landmark.HasField('presence') and landmark.presence < PRESENCE_THRESHOLD)):
                            coords = mp_drawing._normalized_to_pixel_coordinates(
                                landmark.x, landmark.y, width, height)
                            if coords:
                                ldmks[idx, 0] = coords[1]
                                ldmks[idx, 1] = coords[0]
                    ### skin extraction ###
                    cropped_skin_im, full_skin_im = skin_ex.extract_skin(
                        image, ldmks)
                else:
                    cropped_skin_im = np.zeros_like(image)
                    full_skin_im = np.zeros_like(image)
                ### sig computing ###
                for idx in self.ldmks:
                    magic_ldmks.append(ldmks[idx])
                magic_ldmks = np.array(magic_ldmks, dtype=np.float32)
                temp = sig_ext_met(magic_ldmks, full_skin_im, ldmks_regions,
                                   np.int32(SignalProcessingParams.RGB_LOW_TH), np.int32(SignalProcessingParams.RGB_HIGH_TH))
                sig.append(temp)
                # visualize patches and skin
                if self.visualize_skin == True:
                    self.visualize_skin_collection.append(full_skin_im)
                if self.visualize_landmarks == True:
                    annotated_image = full_skin_im.copy()
                    color = np.array([self.font_color[0],
                                      self.font_color[1], self.font_color[2]], dtype=np.uint8)
                    for idx in self.ldmks:
                        cv2.circle(
                            annotated_image, (int(ldmks[idx, 1]), int(ldmks[idx, 0])), radius=0, color=self.font_color, thickness=-1)
                        if self.visualize_landmarks_number == True:
                            cv2.putText(annotated_image, str(idx),
                                        (int(ldmks[idx, 1]), int(ldmks[idx, 0])), cv2.FONT_HERSHEY_SIMPLEX, self.font_size,  self.font_color,  1)
                    if self.visualize_patch == True:
                        if region_type == "squares":
                            sides = np.array([self.square] * len(magic_ldmks))
                            annotated_image = draw_rects(
                                annotated_image, np.array(magic_ldmks[:, 1]), np.array(magic_ldmks[:, 0]), sides, sides, color)
                        elif region_type == "rects":
                            annotated_image = draw_rects(
                                annotated_image, np.array(magic_ldmks[:, 1]), np.array(magic_ldmks[:, 0]), np.array(self.rects[:, 0]), np.array(self.rects[:, 1]), color)
                    self.visualize_landmarks_collection.append(
                        annotated_image)
                ### loop break ###
                if self.tot_frames is not None and self.tot_frames > 0 and processed_frames_count >= self.tot_frames:
                    break
        sig = np.array(sig, dtype=np.float32)
        return np.copy(sig[:, :, 2:])


logger = logging.getLogger(__name__)


# cpu_ICA vs cpu_PBV = cpu_PBV
# cpu_PBV vs cpu_CHROM = cpu_PBV
# cpu_PBV vs cpu_OMIT = cpu_PBV
# Winner - cpu_PBV


def get_bpm_with_pbv(
        cuda: bool = True,
        winsize: int = 4,
) -> tuple:
    """
    Извлекает пульс объёма крови (BVP) из видеофайла и оценивает количество ударов в минуту (BPM).

    Args:
        videoFileName (str): Путь к видеофайлу.
        cuda (bool, опционально): Флаг для использования GPU для обработки. По умолчанию True.
        winsize (int, опционально): Размер окна для обработки сигнала. По умолчанию 4.

    Returns:
        tuple: Кортеж, содержащий извлечённый BVP, временные метки и BPM.

    Raises:
        AssertionError: Если видеофайл не существует.

    """

    # Константы
    class Constants:
        patch_size = 30
        RGB_LOW_HIGH_TH = (75, 230)
        Skin_LOW_HIGH_TH = (75, 230)
        movement_thrs = [10, 5, 2]  # или [15, 15, 15]

    filter = Filter()
    client = filter.create(ip="192.168.43.96")
    sig_processing = NewSignalProcessing(filter, client)

    if cuda:
        logger.debug("Использование GPU")
        sig_processing.display_cuda_device()
        sig_processing.choose_cuda_device(0)
    target_device = "GPU" if cuda else "CPU"

    # Извлекаем зону кожного покрова (region of interest - ROI)
    # Метод ROI: convexhull
    sig_processing.set_skin_extractor(SkinExtractionConvexHull(target_device))

    # Подход ROI: patches
    sig_processing.set_landmarks(vhr_ldmks_list)
    sig_processing.set_square_patches_side(float(Constants.patch_size))

    # Устанавливаем параметры обработчиков
    SignalProcessingParams.RGB_LOW_TH = Constants.RGB_LOW_HIGH_TH[0]
    SignalProcessingParams.RGB_HIGH_TH = Constants.RGB_LOW_HIGH_TH[1]
    SkinProcessingParams.RGB_LOW_TH = Constants.Skin_LOW_HIGH_TH[0]
    SkinProcessingParams.RGB_HIGH_TH = Constants.Skin_LOW_HIGH_TH[1]

    logger.info(f"Обработка видеопотока")

    # Ставим 0, чтобы обработать все доступные кадры
    sig_processing.set_total_frames(0)
    fps = filter.get_fps()
    # Извлекаем patches из видео
    sig= sig_processing.extract_patches("squares", "mean")

    # Разбиваем на перекрывающиеся временные промежутки по 3 RGB каналам
    windowed_sig, timesES = sig_windowing(sig, winsize, 1, fps)

    logger.debug(f" - Количество окон = {len(windowed_sig)}")
    logger.debug(
        f" - Размер окна: (#ROI, #landmarks, #frames) = {windowed_sig[0].shape}"
    )

    # Применяем алгоритмы фильтрации к полученному сигналу
    filter_params = {
        "minHz": 0.6,  # Минимальное значение пульса в герцах
        "maxHz": 4,  # Максимальное значение пульса в герцах
        "fps": "adaptive",
        "order": 6,
    }
    filtered_windowed_sig = apply_filter(
        windowed_sig,
        BPfilter,
        fps=fps,
        params=filter_params,
    )

    logger.debug(" - Применен предварительный фильтр: BPfilter")

    # Извлекаем линию (данные) пульса объёма крови
    logger.info("Извлечение BVP методом 'cpu_PBV' ...")

    bvps_win_m = RGB_sig_to_BVP(
        filtered_windowed_sig,
        fps,
        device_type="cpu",
        method=cpu_PBV,
        params={},
    )

    # Теперь анализируем количество ударов в минуту (BPM) по полученной линии пульса
    logger.info("Расчёт BPM...")

    # - Используем landmarks от mediapipe для компенсации движения лица
    ma = MotionAnalysis(sig_processing, winsize, fps)

    bpmES = BPM_clustering(
        ma,
        bvps_win_m,
        fps,
        winsize,
        movement_thrs=Constants.movement_thrs,
        opt_factor=0.5,
    )
    # ГОТОВО!
    logger.info("ГОТОВО!")

    return bvps_win_m, timesES, bpmES


def process_pulse_info(
        bpm: list, base_offset: int = 10, show_plot: bool = True, plot_path: str = None
) -> tuple:
    """Выполнить оценку полученных значений пульса.

    Args:
        bpm (list): Список исходных значений.
        base_offset (int, optional): Смещение для значений пульса. Defaults to 10.
        show_plot (bool, optional): Показывать график или нет. По умолчанию True.
        plot_path (str, optional): Путь для сохранения графика. По умолчанию None.

    Raises:
        ValueError: Если список bpm пуст.
        ValueError: Если base_offset меньшн минимального значения пульса
        AssertionError: Если base_offset не в диапазоне от -40 до 40

    Returns:
        tuple: _description_
    """
    if not bpm.any():
        raise ValueError("bpm list is empty!")

    if len(bpm) < 4:
        # Random Extrapolation
        bpm.extend(choice(bpm) for _ in range(5 - len(bpm)))

    assert (
            base_offset > -40 and base_offset < 40
    ), "base_offset must be between -40 and 40"

    bpm = add_offset_to_values(bpm, base_offset)  # Добавляем смещение

    if min(bpm) < 0:
        raise ValueError("bpm must be positive! Probably, offset is too large.")

    base_mean = round(statistics.median(bpm), 2)  # Медианное значение
    mids, tnums, tvals = get_plot_tops_n_times(bpm, 1)  # Верхушки графика

    trend = get_trend(tvals)  # Определяем тренд
    trend_text = {0: "No trend", 1: "Uptrend", -1: "Downtrend"}[trend]

    ordered_highs = get_largest_serially(tvals, 3)
    high_med = round(statistics.median(ordered_highs), 2)

    logger.info("Результат анализа пульса:")
    logger.info(f"- Общая медиана: {base_mean}")
    logger.info(f"- Медиана ({len(tvals)}) верхушек: {high_med}")
    logger.info(f"- Тренд: {trend_text}")

    plt.figtext(0.15, 0.84, "Результат анализа пульса:")
    plt.figtext(0.15, 0.80, f"- Общая медиана: {base_mean}")
    plt.figtext(0.15, 0.76, f"- Медиана ({len(tvals)}) верхушек: {high_med}")
    plt.figtext(0.15, 0.72, f"- Тренд: {trend_text}")

    plt.plot(bpm, color="b")
    plt.plot(
        [(i + 1 + i) / 2 for i in range(len(mids))],
        mids,
        marker="x",
        color="r",
    )

    plt.scatter(tnums, tvals, marker="o", color="g", zorder=2)
    plt.grid(True)

    if plot_path:
        plt.savefig(plot_path, bbox_inches="tight")
    if show_plot:
        plt.show(block=False)
        # plt.pause(20)

    return base_mean, trend, high_med, mids, tvals


def evaluate_pulse_results(
        base_mean: float, trend: int, high_med: float, midpoints: list, tops_values: list
) -> int:
    """Выполнить оценку по шкале баллов на основе полученных данных о значениях и изменениях пульса

    Args:
        base_mean (float): _description_
        trend (int): _description_
        high_med (float): _description_
        midpoints (list): _description_
        tops_values (list): _description_

    Returns:
        int: _description_
    """
    points = 0
    logger.info("Оценка значений пульса:")

    if (high_med - base_mean > 12 and base_mean > 80) or max(midpoints) - min(
            midpoints
    ) > 12:
        points -= 1
        logger.info("- Пульс не стабилен! (-1 балл)")

    if high_med > 90:
        points -= 1
        logger.info("- Высокий фон пульса! (-1 балл)")

    if max(tops_values) > 102:
        points -= 1
        logger.info(f"- Найден высокий пик {max(tops_values)}! (-1 балл)")

    if trend == 1:
        points -= 1
        # Пульс увеличивается - возможно, человек начинает волноваться.
        logger.info("- Восходящий тренд! (-1 балл)")

    elif trend == -1:
        points += 1
        # Пульс уменьшается - возможно, человек просто запыхался.
        logger.info("- Нисходящий тренд! (+1 балл)")

    else:
        logger.info("--- Тренд изменений отсутствует. Эта метрика не учитывается. ---")

    return points


if __name__ == "__main__":
    pass