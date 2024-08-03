import logging
import os

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

from .helpers_code import vhr_ldmks_list

logger = logging.getLogger(__name__)


def get_bpm_with_pbv(
    videoFileName,
    cuda=True,
    winsize=4,
):
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

    Режим подробного логирования завиит от уровня логирования DEBUG в модуле logging.
    """

    # Константы
    patch_size = 30
    RGB_LOW_HIGH_TH = (75, 230)
    Skin_LOW_HIGH_TH = (75, 230)
    movement_thrs = [10, 5, 2]  # или [15, 15, 15]

    verb = (True if logger.level == logging.DEBUG else False,)

    assert os.path.isfile(videoFileName), "Видео файл не существует!"
    sig_processing = SignalProcessing()

    if cuda:
        logger.debug("Использование GPU")
        if verb:
            sig_processing.display_cuda_device()
        sig_processing.choose_cuda_device(0)
    target_device = "GPU" if cuda else "CPU"

    # Извлекаем зону кожного покрова (region of interest - ROI)
    # Метод ROI: convexhull
    sig_processing.set_skin_extractor(SkinExtractionConvexHull(target_device))

    # Подход ROI: patches
    sig_processing.set_landmarks(vhr_ldmks_list)
    sig_processing.set_square_patches_side(float(patch_size))

    # Устанавливаем параметры обработчиков
    SignalProcessingParams.RGB_LOW_TH = RGB_LOW_HIGH_TH[0]
    SignalProcessingParams.RGB_HIGH_TH = RGB_LOW_HIGH_TH[1]
    SkinProcessingParams.RGB_LOW_TH = Skin_LOW_HIGH_TH[0]
    SkinProcessingParams.RGB_HIGH_TH = Skin_LOW_HIGH_TH[1]

    logger.info("Обработка видео: " + videoFileName)

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
    filtered_windowed_sig = apply_filter(
        windowed_sig,
        BPfilter,
        fps=fps,
        params={
            "minHz": 0.6,  # Минимальное значение пульса в герцах
            "maxHz": 4,  # Максимальное значение пульса в герцах
            "fps": "adaptive",
            "order": 6,
        },
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
        movement_thrs=movement_thrs,
        opt_factor=0.5,
    )
    # ГОТОВО!
    logger.info("ГОТОВО!")

    return bvps_win_m, timesES, bpmES
