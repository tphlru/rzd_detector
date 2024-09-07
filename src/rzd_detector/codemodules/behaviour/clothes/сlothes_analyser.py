# CornerNet-Lite project - https://github.com/princeton-vl/CornerNet-Lite
# DeepFashoin2 Dataset - https://github.com/switchablenorms/DeepFashion2
import os
import logging

import requests
from datetime import datetime

import cv2
import numpy as np
from typing import List, Optional

from .cornernetlib.core.vis_utils import draw_bboxes
from .cornernetlib.core.detectors import CornerNet_Saccade

logger = logging.getLogger(__name__)


class_list = [
    "long_sleeve_dress",
    "long_sleeve_outwear",
    "long_sleeve_top",
    "short_sleeve_dress",
    "short_sleeve_outwear",
    "short_sleeve_top",
    "shorts",
    "skirt",
    "sling",
    "sling_dress",
    "trousers",
    "vest",
    "vest_dress",
]


def _get_true_predictions(predictions, thresh):
    true_predictions = []
    for cat in predictions:
        keep_index = predictions[cat][:, -1] > thresh
        if len(predictions[cat][keep_index]) == 0:
            continue
        true_predictions.append(cat)
    return true_predictions


def get_clothes(
    source_img: np.ndarray,
    thresh: float = 0.5,
    show: bool = False,
    fname: Optional[str] = None,
) -> List[str]:
    """Определить, какая одежда одета на чловека по фотографии.
    Используем модель cornernet, обученную на DeepFashion2

    Args:
        source_img (np.ndarray): Исходное изображение. Можно получить с помощью cv2.imread
        thresh (float, optional): Пороговое значение вероятности. По умолчанию 0.5.
        show (bool, optional): Показывать ли результат на картинке. По умолчанию False.
        fname (Optional[str], optional): Имя файла для сохранения результата на картинке. По умолчанию None.

    Raises:
        ValueError: Если изображение пустое или отсутствует.
        FileNotFoundError: Если модель не найдена.

    Returns:
        List[str]: Список, содержащий идентификаторы одежды.
    """
    if source_img is None:
        raise ValueError("Image is empty!")
    # Создаём пути относительно модуля
    base_path = os.path.abspath(os.path.dirname(__file__))
    model_path = os.path.join(
        base_path,
        "cornernetlib",
        "models",
        "cache",
        "nnet",
        "CornerNet_Saccade",
        "CornerNet_Saccade_best.pkl",
    )
    # Проверяем наличие модели
    if not os.path.isfile(model_path):
        raise FileNotFoundError(
            "Pretrained CornerNet model not found. Please reinstall the package to download the model."
        )
    # Инициализируем детектор
    detector = CornerNet_Saccade(
        test=True, class_list=class_list, model_path=model_path
    )
    raw_result = detector(source_img)  # Получаем сырые результаты предсказания

    featured_categories = _get_true_predictions(raw_result, thresh)

    # Если слишком много одежды, поднимаем порог на 0.2
    while len(featured_categories) > 5 and thresh < 0.9:
        thresh += 0.25
        logger.warning(f"Слишком много одежды, попытка увеличения порога до {thresh}")
        featured_categories = _get_true_predictions(raw_result, thresh)

    # Если нет одежды на изображении, снижаем порог на 0.04
    while len(featured_categories) == 0 and thresh > 0.2:
        thresh -= 0.04
        logger.warning(
            f"Нет одежды на изображении, попытка снижения порога до {thresh}"
        )
        featured_categories = _get_true_predictions(raw_result, thresh)

    logger.info(f"Определен тип одежды: {featured_categories}")
    out_image = draw_bboxes(source_img, raw_result, thresh=thresh)

    if fname:
        cv2.imwrite(fname, out_image)
    if show:
        cv2.imshow("Output Image", out_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return featured_categories


def is_dressed_for_weather(clothes: List[str], temperature: float, season: str) -> bool:
    """Определить, подходит ли под текущую погоду (температуру и время года)

    Args:
        clothes (list): Список, содержащий идентификаторы одежды
        temperature (float): Температура воздуха в градусах Цельсия
        season (str): Текущий сезон - winter, summer, spring, autumn

    Returns:
        bool: True, если одежда подходит под текущую погоду, иначе False
    """
    # Логика для каждой категории одежды
    cold = [
        "long_sleeve_outwear",
        "long_sleeve_top",
        "trousers",
    ]
    cool = [
        "long_sleeve_dress",
        "long_sleeve_top",
        "trousers",
        "short_sleeve_outwear",
        "long_sleeve_outwear",
        "skirt",
    ]
    warm = [
        "short_sleeve_top",
        "short_sleeve_dress",
        "shorts",
        "skirt",
        "sling",
        "sling_dress",
        "vest",
    ]

    # Проверяем температуру и соответствующую одежду
    if temperature < -10:
        allowed_clothes = cold
        denied_clothes = warm
    elif 0 <= temperature < 10:
        allowed_clothes = cool
    else:
        allowed_clothes = warm
        denied_clothes = cold

    if season == "summer":
        denied_clothes = denied_clothes + cold
    elif season == "winter":
        denied_clothes = denied_clothes + warm
    elif season in {"spring", "autumn"}:
        allowed_clothes = allowed_clothes + cool
        denied_clothes = list(set(denied_clothes) - set(cool))

    return all(
        item in allowed_clothes and item not in denied_clothes for item in clothes
    )


def get_weather(API_KEY, UNITS="metric", defaults=None, CITY="Moscow"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&APPID={API_KEY}&units={UNITS}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        # Получаем текущую температуру
        temperature = data["main"]["temp"]
        # Получаем текущий месяц для определения сезона
        month = datetime.now().month
        season = get_season(month)

        return temperature, season
    else:
        logger.error("Ошибка при получении данных с OpenWeatherMap")
        return defaults


def get_season(month):
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
