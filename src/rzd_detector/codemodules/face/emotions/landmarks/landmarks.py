import cv2
import mediapipe as mp
import numpy as np
import logging

logger = logging.getLogger(__name__)


def _load_image(image_input):
    """Загрузка изображения из файла или OpenCV.

    Args:
        image_input (str или numpy.ndarray): Путь к файлу изображения или изображение в формате OpenCV.

    Returns:
        загруженное изображение (BGR)
    """
    import os

    if isinstance(image_input, str):
        if not os.path.isfile(image_input):
            raise FileNotFoundError(f"Файл не найден: {image_input}")
        return cv2.imread(image_input)
    elif isinstance(image_input, np.ndarray):
        return image_input
    else:
        raise ValueError(
            "Входные данные должны быть строкой (путь к файлу) или массивом NumPy."
        )


def process_image(
    img,
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.4,
):
    """Обрабатывает изображение для извлечения координат лицевых маркеров.

    Args:
        img (numpy.ndarray): Изображение в формате OpenCV.
        static_image_mode (bool): Режим обработки статического изображения.
        max_num_faces (int): Максимальное количество лиц для обнаружения.
        refine_landmarks (bool): Уточнять ли маркеры.
        min_detection_confidence (float): Минимальная уверенность для обнаружения.

    Returns:
        list: Список координат маркеров лица или None, если лицо не обнаружено.
    """
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=static_image_mode,
        max_num_faces=max_num_faces,
        refine_landmarks=refine_landmarks,
        min_detection_confidence=min_detection_confidence,
    ) as face_mesh:
        results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return None

    return results.multi_face_landmarks[0].landmark


def curved_crop_and_mask(
    image, landmarks, hide_eyes=True, hide_mouth=True, curve_crop=True, mouth_k=0.5
):
    """Выполняет кривую обрезку и маскирование для рта или глаз.

    Args:
        image (numpy.ndarray): Исходное изображение.
        landmarks (list): Список координат маркеров лица.
        hide_eyes (bool): Скрыть ли глаза.
        hide_mouth (bool): Скрыть ли рот.
        curve_crop (bool): Выполнить кривую обрезку.

    Returns:
        numpy.ndarray: Изображение с примененной маской и обрезкой.
    """
    face_crop, local_landmarks = crop_face(image, landmarks)
    mask = create_mask(
        local_landmarks, hide_eyes, hide_mouth, face_crop, mouth_k=mouth_k
    )
    return apply_mask_and_crop(face_crop, local_landmarks, mask, curve_crop)


def crop_face(image, landmarks):
    """Обрезает изображение по границам маркеров лица.

    Args:
        image (numpy.ndarray): Исходное изображение.
        landmarks (list): Список координат маркеров лица.

    Returns:
        tuple: (numpy.ndarray, list) - Кортеж из обрезанного изображения и локальных координат.
    """
    height, width, _ = image.shape
    coords = np.array([(lm.x, lm.y, lm.z) for lm in landmarks])
    # Векторизованное масштабирование
    coords[:, 0] = np.multiply(coords[:, 0], width)
    coords[:, 1] = np.multiply(coords[:, 1], height)

    min_x, min_y = int(np.min(coords[:, 0])), int(np.min(coords[:, 1]))
    max_x, max_y = int(np.max(coords[:, 0])), int(np.max(coords[:, 1]))

    face_crop = image[min_y:max_y, min_x:max_x]
    local_landmarks = [(pt[0] - min_x, pt[1] - min_y, pt[2]) for pt in coords]
    return face_crop, local_landmarks


def create_mask(local_landmarks, hide_eyes, hide_mouth, face_crop, mouth_k=0.5):
    """Создает маску для скрытия глаз и/или рта.

    Args:
        local_landmarks (list): Локальные координаты маркеров лица.
        hide_eyes (bool): Скрыть ли глаза.
        hide_mouth (bool): Скрыть ли рот.
        face_crop (numpy.ndarray): Обрезанное изображение лица.
        mouth_k (float): Коэффициент для расширения маски рта.

    Returns:
        numpy.ndarray: Маска для скрытия областей.
    """
    mask = np.zeros(face_crop.shape[:2], dtype=np.uint8)

    if hide_eyes:
        left_eye_indices = [
            33,
            7,
            163,
            144,
            145,
            153,
            154,
            155,
            133,
            173,
            157,
            158,
            159,
            160,
            161,
            246,
        ]
        right_eye_indices = [
            263,
            249,
            390,
            373,
            374,
            380,
            381,
            382,
            362,
            398,
            384,
            385,
            386,
            387,
            388,
            466,
        ]
        left_eye_poly = np.array(
            [
                [int(local_landmarks[i][0]), int(local_landmarks[i][1])]
                for i in left_eye_indices
            ],
            np.int32,
        )
        right_eye_poly = np.array(
            [
                [int(local_landmarks[i][0]), int(local_landmarks[i][1])]
                for i in right_eye_indices
            ],
            np.int32,
        )
        cv2.fillPoly(mask, [left_eye_poly, right_eye_poly], 255)

    if hide_mouth:
        mouth_indices = [
            78,
            95,
            88,
            178,
            87,
            14,
            317,
            402,
            318,
            324,
            308,
            415,
            310,
            311,
            312,
            13,
            82,
        ]
        mouth_poly = np.array(
            [
                [int(local_landmarks[i][0]), int(local_landmarks[i][1])]
                for i in mouth_indices
            ],
            np.int32,
        )
        # Создаем отдельную маску для области рта
        mouth_mask = np.zeros(face_crop.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mouth_mask, [mouth_poly], 255)

        # Определяем размер ядра на основе mouth_k
        kernel_size = max(1, int(mouth_k * 5))
        if kernel_size % 2 == 0:
            kernel_size += 1
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
        )
        mouth_mask = cv2.dilate(mouth_mask, kernel, iterations=1)

        # Объединяем маску рта с основной маской
        mask = cv2.bitwise_or(mask, mouth_mask)

    return mask


def apply_mask_and_crop(face_crop, local_landmarks, mask, curve_crop):
    """Применяет маску и выполняет кривую обрезку изображения.

    Args:
        face_crop (numpy.ndarray): Обрезанное изображение лица.
        local_landmarks (list): Локальные координаты маркеров лица.
        mask (numpy.ndarray): Маска для скрытия глаз и/или рта.
        curve_crop (bool): Выполнить кривую обрезку.

    Returns:
        numpy.ndarray: Изображение с примененной маской и обрезкой.
    """
    if curve_crop:
        face_mask = np.zeros(face_crop.shape[:2], dtype=np.uint8)
        hull = cv2.convexHull(np.array(local_landmarks)[:, :2].astype(np.int32))
        cv2.fillPoly(face_mask, [hull], 255)

        # Создаем результирующее изображение сразу с белым фоном
        result = np.full_like(face_crop, 255)
        # Копируем только нужные области
        np.copyto(result, face_crop, where=(face_mask[:, :, None] == 255))
    else:
        result = face_crop.copy()
    # Применяем маску глаз/рта
    result[mask == 255] = 255
    return result


def process_landmarks(
    image,
    save_path=None,
    hide_eyes=True,
    hide_mouth=True,
    mouth_k=0.5,
    curve_crop=True,
    return_image=False,
    return_raw=False,
    verbose=False,
):
    """Обрабатывает лицевые маркеры и выполняет модификации лица.

    Обрабатывает входное изображение для обнаружения лицевых маркеров и применяет
    опциональные модификации, такие как скрытие глаз/рта и криволинейная обрезка.

    Args:
        image (Union[str, numpy.ndarray]): Путь к изображению или массив OpenCV
        save_path (Optional[str]): Путь для сохранения обработанного изображения
        hide_eyes (bool): Скрывать ли области глаз
        hide_mouth (bool): Скрывать ли область рта
        mouth_k (float): Коэффициент для закрытия губ (0-1 и больше)
        curve_crop (bool): Применять ли криволинейную обрезку лица
        return_image (bool): Возвращать ли обработанное изображение вместе с маркерами
        return_raw (bool): Возвращать ли landmarks в необработанном виде
            (<class 'google._upb._message.RepeatedCompositeContainer'>)
        verbose (bool): Показывать ли результирующее изображение

    Returns:
        Union[Tuple[list, numpy.ndarray], list, None]:
            - Если return_image=True: Кортеж (маркеры, обработанное_изображение)
            - Если return_image=False: Список маркеров (numpy.ndarray x, y, z)
            - None, если лицо не обнаружено

    Raises:
        FileNotFoundError: Если путь к изображению недействителен
        ValueError: Если входное изображение не является ни путём, ни массивом numpy
    """
    image = _load_image(image)
    landmarks = process_image(image)
    if landmarks is None:
        return None
    result_image = curved_crop_and_mask(
        image,
        landmarks,
        hide_eyes=hide_eyes,
        hide_mouth=hide_mouth,
        curve_crop=curve_crop,
        mouth_k=mouth_k,
    )

    if verbose:
        cv2.imshow("Result", result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if save_path:
        cv2.imwrite(save_path, result_image)

    if return_raw is False:
        landmarks = np.array([(lm.x, lm.y, lm.z) for lm in landmarks])

    return (landmarks, result_image) if return_image else landmarks
