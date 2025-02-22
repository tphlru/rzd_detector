import cv2
import mediapipe as mp
import numpy as np
import logging
import os

from typing import Union

logger = logging.getLogger(__name__)


class FaceLandmarksProcessor:
    LEFT_EYE_INDICES = [
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
    RIGHT_EYE_INDICES = [
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
    MOUTH_INDICES = [
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

    def __init__(self, verbose=False):
        """Инициализирует процессор с возможностью вывода отладочной информации."""
        self.verbose = verbose
        self.mp_face_mesh = mp.solutions.face_mesh
        # Will store crop parameters from crop_face for later use.
        self.last_crop_info = None

    def _load_image(self, image_input):
        """Загрузка изображения из файла или OpenCV.

        Args:
            image_input (str или numpy.ndarray): Путь к файлу изображения или изображение в формате OpenCV.

        Returns:
            загруженное изображение (BGR)
        """
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
        self,
        img,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.4,
    ):
        """Обрабатывает изображение для извлечения координат лицевых маркеров.        

        Args:
            img (numpy.ndarray): Изображение в формате OpenCV.
            max_num_faces (int): Максимальное количество лиц для обнаружения.
            refine_landmarks (bool): Уточнять ли маркеры.
            min_detection_confidence (float): Минимальная уверенность для обнаружения.

        Returns:
            list: Список координат маркеров лица или None, если лицо не обнаружено.
        """
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        with self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
        ) as face_mesh:
            results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None
        if len(results.multi_face_landmarks) > 1:
            return results.multi_face_landmarks
        else:
            return results.multi_face_landmarks[0].landmark

    def curved_crop_and_mask(
        self,
        image,
        landmarks,
        hide_eyes=True,
        hide_mouth=True,
        curve_crop=True,
        mouth_k=0.5,
        transparent_bg=False,
    ):
        """Выполняет кривую обрезку и маскирование для рта или глаз.

        Args:
            image (numpy.ndarray): Исходное изображение.
            landmarks (list): Список координат маркеров лица.
            hide_eyes (bool): Скрыть ли глаза.
            hide_mouth (bool): Скрыть ли рот.
            curve_crop (bool): Выполнить кривую обрезку.
            transparent_bg (bool): Использовать прозрачный фон вместо белого.

        Returns:
            numpy.ndarray: Изображение с примененной маской и обрезкой.
        """
        face_crop, local_landmarks = self.crop_face(image, landmarks)
        mask = self.create_mask(
            local_landmarks, hide_eyes, hide_mouth, face_crop, mouth_k=mouth_k
        )
        return self.apply_mask_and_crop(
            face_crop, local_landmarks, mask, curve_crop, transparent_bg=transparent_bg
        )

    def crop_face(self, image, landmarks):
        """Обрезает изображение по границам маркеров лица.

        Args:
            image (numpy.ndarray): Исходное изображение.
            landmarks (list): Список координат маркеров лица.

        Returns:
            tuple: (numpy.ndarray, list) - Кортеж из обрезанного изображения и локальных координат.
        """
        height, width, _ = image.shape
        coords = np.array([(lm.x, lm.y, lm.z) for lm in landmarks])
        coords[:, 0] = np.multiply(coords[:, 0], width)
        coords[:, 1] = np.multiply(coords[:, 1], height)

        min_x, min_y = int(np.min(coords[:, 0])), int(np.min(coords[:, 1]))
        max_x, max_y = int(np.max(coords[:, 0])), int(np.max(coords[:, 1]))

        face_crop = image[min_y:max_y, min_x:max_x]
        local_landmarks = [(pt[0] - min_x, pt[1] - min_y, pt[2]) for pt in coords]
        # Save crop info to allow full mask recovery later.
        self.last_crop_info = {
            "min_x": min_x,
            "min_y": min_y,
            "local_landmarks": local_landmarks,
        }
        return face_crop, local_landmarks

    def create_mask(
        self, local_landmarks, hide_eyes, hide_mouth, face_crop, mouth_k=0.5
    ):
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
            left_eye_poly = np.array(
                [
                    [int(local_landmarks[i][0]), int(local_landmarks[i][1])]
                    for i in self.LEFT_EYE_INDICES
                ],
                np.int32,
            )
            right_eye_poly = np.array(
                [
                    [int(local_landmarks[i][0]), int(local_landmarks[i][1])]
                    for i in self.RIGHT_EYE_INDICES
                ],
                np.int32,
            )
            cv2.fillPoly(mask, [left_eye_poly, right_eye_poly], 255)

        if hide_mouth:
            mouth_poly = np.array(
                [
                    [int(local_landmarks[i][0]), int(local_landmarks[i][1])]
                    for i in self.MOUTH_INDICES
                ],
                np.int32,
            )
            mouth_mask = np.zeros(face_crop.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mouth_mask, [mouth_poly], 255)

            kernel_size = max(1, int(mouth_k * 5))
            if kernel_size % 2 == 0:
                kernel_size += 1
            kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
            )
            mouth_mask = cv2.dilate(mouth_mask, kernel, iterations=1)
            mask = cv2.bitwise_or(mask, mouth_mask)

        return mask

    def apply_mask_and_crop(
        self, face_crop, local_landmarks, mask, curve_crop, transparent_bg=False
    ):
        """Применяет маску и выполняет кривую обрезку изображения.

        Args:
            face_crop (numpy.ndarray): Обрезанное изображение лица.
            local_landmarks (list): Локальные координаты маркеров лица.
            mask (numpy.ndarray): Маска для скрытия глаз и/или рта.
            curve_crop (bool): Выполнить кривую обрезку.
            transparent_bg (bool): Использовать прозрачный фон вместо белого.

        Returns:
            numpy.ndarray: Изображение с примененной маской и обрезкой.
        """
        if transparent_bg:
            # Convert to BGRA
            result = np.zeros((*face_crop.shape[:2], 4), dtype=np.uint8)
            result[..., :3] = face_crop
            result[..., 3] = 255  # Full opacity initially
        else:
            result = np.full_like(face_crop, 255)

        if curve_crop:
            face_mask = np.zeros(face_crop.shape[:2], dtype=np.uint8)
            hull = cv2.convexHull(np.array(local_landmarks)[:, :2].astype(np.int32))
            cv2.fillPoly(face_mask, [hull], 255)

            if transparent_bg:
                # Set alpha channel to 0 (transparent) outside face area
                result[..., 3] = face_mask
                # Copy face area
                np.copyto(
                    result[..., :3], face_crop, where=(face_mask[:, :, None] == 255)
                )
            else:
                np.copyto(result, face_crop, where=(face_mask[:, :, None] == 255))

        # Handle masked areas (eyes/mouth)
        if transparent_bg:
            result[mask == 255, 3] = 0  # Make masked areas transparent
        else:
            result[mask == 255] = 255  # Make masked areas white

        return result

    def process_landmarks(
        self,
        image: Union[str, np.ndarray],
        save_path: str = None,
        hide_eyes=True,
        hide_mouth=True,
        mouth_k=0.5,
        curve_crop=True,
        return_image=False,
        return_raw=False,
        transparent_bg=False,
        max_faces_count = 1
    ) -> "FaceLandmarksResult":
        """Обрабатывает лицевые маркеры и выполняет модификации.

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
        Returns:
            FaceLandmarksResult: Объект результата работы с методами для получения изображения, координат и маски.
        Raises:
            FileNotFoundError: Если путь к изображению недействителен
            ValueError: Если входное изображение не является ни путём, ни массивом numpy
        """
        original_image = self._load_image(image)
        multi_face_landmarks = self.process_image(original_image, max_num_faces=max_faces_count)
        if multi_face_landmarks is None:
            return None
        elif type(multi_face_landmarks) == list:
            for landmark in multi_face_landmarks:
                landmark.landmark



        else:
            result_image = self.curved_crop_and_mask(
                original_image,
                multi_face_landmarks,
                hide_eyes=hide_eyes,
                hide_mouth=hide_mouth,
                curve_crop=curve_crop,
                mouth_k=mouth_k,
                transparent_bg=transparent_bg,
            )

        if self.verbose:
            cv2.imshow("Result", result_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        raw = None
        if not return_raw:
            raw = np.array([(lm.x, lm.y, lm.z) for lm in landmarks])
        # Create the result instance and automatically call save if save_path is provided.
        result_obj = FaceLandmarksResult(
            original_image=original_image,
            landmarks=np.array([(lm.x, lm.y, lm.z) for lm in landmarks]),
            processed_image=result_image,
            raw=raw,
            _return_image=return_image,
            _last_crop_info=self.last_crop_info,
        )
        if result_obj is None:
            return None
        if save_path:
            try:
                cv2.imwrite(save_path, result_image)
            except Exception as e:
                return None
        return result_obj


class FaceLandmarksResult(FaceLandmarksProcessor):
    """Подкласс, содержащий результаты обработки изображения лицевых маркеров, а также методы доступа к ним.

    Attributes:
        original_image (numpy.ndarray): Исходное изображение.
        landmarks (numpy.ndarray): Координаты маркеров лица.
        processed_image (numpy.ndarray): Обработанное изображение.
        raw (numpy.ndarray): Необработанные координаты маркеров лица (None если отключено).

    Methods:
        get_full_mask(): Возвращает маску исходного изображения, где область лица выделена белым цветом.
        save_image(path): Сохраняет обработанное изображение по указанному пути.
    """

    def __init__(
        self,
        original_image,
        landmarks,
        processed_image,
        raw,
        _return_image,
        _last_crop_info,
    ):
        # Инициализируем родительский класс, чтобы иметь доступ к его методам и полям.
        super().__init__()
        self.original_image = original_image
        self.landmarks = landmarks
        self.processed_image = processed_image if _return_image else None
        self.raw = raw
        # Сохраняем данные кропа, чтобы в дальнейшем восстановить координаты лица в полном изображении.
        self.last_crop_info = _last_crop_info

    def get_full_mask(self):
        """Возвращает маску исходного изображения, где область лица выделена белым цветом.
        Маска вычисляется с использованием сохраненных координат кропа.
        """
        if not self.last_crop_info:
            return None
        h, w = self.original_image.shape[:2]
        min_x = self.last_crop_info["min_x"]
        min_y = self.last_crop_info["min_y"]
        local_landmarks = self.last_crop_info["local_landmarks"]
        # Восстанавливаем глобальные координаты: прибавляем смещение.
        global_pts = np.array(
            [[int(pt[0] + min_x), int(pt[1] + min_y)] for pt in local_landmarks],
            np.int32,
        )
        hull = cv2.convexHull(global_pts)
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [hull], 255)
        return mask

    def save_image(self, path):
        """Сохраняет обработанное изображение по указанному пути."""
        cv2.imwrite(path, self.processed_image)
