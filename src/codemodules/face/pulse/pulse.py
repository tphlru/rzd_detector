import logging
import os
import statistics
import matplotlib.pyplot as plt


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
from pyVHR.extraction.utils import MotionAnalysis, get_fps, sig_windowing

from .helpers_code import vhr_ldmks_list, get_largest_serially
from rzd_detector.common.utils import (
    add_offset_to_values,
    get_plot_tops_n_times,
    get_trend,
)

logger = logging.getLogger(__name__)

# cpu_ICA vs cpu_PBV = cpu_PBV
# cpu_PBV vs cpu_CHROM = cpu_PBV
# cpu_PBV vs cpu_OMIT = cpu_PBV
# Winner - cpu_PBV


def get_bpm_with_pbv(
    videoFileName: str,
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

    if not os.path.exists(videoFileName):
        raise FileNotFoundError("Видео файл не существует!")

    sig_processing = SignalProcessing()

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

    logger.info(f"Обработка видео: {videoFileName}")

    # Ставим 0, чтобы обработать все доступные кадры
    sig_processing.set_total_frames(0)
    fps = get_fps(videoFileName)  # Частота кадров исходного видео

    # Извлекаем patches из видео
    sig = sig_processing.extract_patches(videoFileName, "squares", "mean")

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

    if not bpm.any():
        raise ValueError("bpm list is empty!")

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
        plt.pause(20)

    return base_mean, trend, high_med


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
    logger.info("Бальная оценка для пульса:")

    if (high_med - base_mean > 12 and base_mean > 80) or max(midpoints) - min(
        midpoints
    ) > 12:
        points += 1
        logger.info("- Пульс не стабилен! (+1 балл)")

    if high_med > 90:
        points += 1
        logger.info("- Высокий фон пульса! (+1 балл)")

    if max(tops_values) > 102:
        points += 1
        logger.info(f"- Найден высокий пик {max(tops_values)}! (+1 балл)")

    if trend == 1:
        points += 1
        # Пульс увеличивается - возможно, человек начинает волноваться.
        logger.info("- Восходящий тренд! (+1 балл)")

    elif trend == -1:
        points -= 1
        # Пульс уменьшается - возможно, человек просто запыхался.
        logger.info("- Нисходящий тренд! (-1 балл)")

    else:
        logger.info("--- Тренд изменений отсутствует. Эта метрика не учитывается. ---")

    return points
