import cv2
import numpy as np
from rzd_detector.codemodules.face.emotions.landmarks import FaceLandmarksProcessor

def crop_video(input_video_path, output_video_path, scale_width=1.5, scale_height=2.0, skip_frames=5):
    # Создание объекта для обработки лицевых маркеров
    processor = FaceLandmarksProcessor(verbose=False)

    # Открытие видео
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Не удалось открыть видео.")
        return

    # Получение информации о видео (разрешение и частота кадров)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Выбираем случайный кадр, например, средний кадр
    middle_frame = frame_count // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
    ret, frame = cap.read()
    if not ret:
        print("Не удалось считать кадр.")
        return

    # Получение размеров из среднего кадра
    frame_height, frame_width, _ = frame.shape

    # Настройка кодека и выходного видео
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Пробуем другой кодек
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    last_landmarks = None  # Переменная для хранения маркеров лица с последнего кадра

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Возвращаемся к началу видео

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Пропускаем кадры
        if frame_count % skip_frames == 0:
            landmarks = processor.process_image(frame)
            if landmarks:
                last_landmarks = landmarks  # Обновляем маркеры лица

        # Если маркеры были найдены, кадрируем изображение
        if last_landmarks:
            coords = np.array([(lm.x, lm.y) for lm in last_landmarks])
            min_x, min_y = np.min(coords[:, 0]), np.min(coords[:, 1])
            max_x, max_y = np.max(coords[:, 0]), np.max(coords[:, 1])

            # Перевод координат в пиксели
            min_x, min_y = int(min_x * frame_width), int(min_y * frame_height)
            max_x, max_y = int(max_x * frame_width), int(max_y * frame_height)

            # Определение области кадрирования
            face_width = max_x - min_x
            face_height = max_y - min_y

            # Увеличение области вокруг лица
            crop_x1 = max(min_x - int(face_width * (scale_width - 1) / 2), 0)
            crop_y1 = max(min_y - int(face_height * (scale_height - 1) / 2), 0)
            crop_x2 = min(max_x + int(face_width * (scale_width - 1) / 2), frame_width)
            crop_y2 = min(max_y + int(face_height * (scale_height - 1) / 2), frame_height)

            # Обрезка изображения
            cropped_frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]

            # Отображаем кадр с выделенной областью лица (для отладки)
            cv2.rectangle(frame, (crop_x1, crop_y1), (crop_x2, crop_y2), (0, 255, 0), 2)  # Зеленая рамка вокруг лица
            for lm in last_landmarks:
                x = int(lm.x * frame_width)
                y = int(lm.y * frame_height)
                cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)  # Красные точки для маркеров

            # # Показываем кадр с маркерами и рамкой
            # cv2.imshow('Processed Frame', frame)
            # cv2.waitKey(1)  # Небольшая задержка для отображения кадра

        else:
            # Если маркеры лица не были найдены, просто пишем оригинальный кадр
            cropped_frame = frame

        out.write(cropped_frame)
        cv2.imshow('Processed Frame', cropped_frame)
        cv2.waitKey(1)  # Небольшая задержка для отображения кадра
        frame_count += 1

    # Закрытие видео
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Пример использования
crop_video('upload/10.mp4', 'upload/cropped.mp4')
