import cv2
import mediapipe as mp
import numpy as np

def crop_face(img, padding=20):
    """Обрезает лицо на изображении и сохраняет результат."""
    # Инициализация MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    face_detector = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    # Загрузка изображения
    if img is None:
        print("Ошибка: не удалось загрузить изображение.")
        return False

    # Конвертация в RGB (MediaPipe работает с RGB)
    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Детекция лица
    results = face_detector.process(image_rgb)

    if not results.detections:
        print("Лицо не найдено.")
        return False

    # Получение координат лица
    h, w, _ = img.shape
    bbox = results.detections[0].location_data.relative_bounding_box
    x_min = int(bbox.xmin * w) - padding
    y_min = int(bbox.ymin * h) - padding
    x_max = int((bbox.xmin + bbox.width) * w) + padding
    y_max = int((bbox.ymin + bbox.height) * h) + padding

    # Ограничение координат в пределах изображения
    x_min, y_min = max(x_min, 0), max(y_min, 0)
    x_max, y_max = min(x_max, w), min(y_max, h)

    # Обрезка лица
    cropped_face = img[y_min:y_max, x_min:x_max]

    return cropped_face

# Пример использования
img = cv2.imread("Scripts/test_files/common/george.jpg")
crop_im = crop_face(img)
cv2.imwrite("Scripts/test_files/common/george_crop.jpg", crop_im)
