import cv2
import random

def is_sharp_frame(frame, threshold=100):
    """
    Проверка кадра на резкость с использованием дисперсии Лапласа.
    Если значение дисперсии больше или равно порогу, кадр считается чётким.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var >= threshold, laplacian_var

def get_random_sharp_frame(cap, start_frame, end_frame, threshold=100, max_attempts=20):
    """
    Поиск случайного чёткого кадра в диапазоне [start_frame, end_frame).
    Проводится не более max_attempts попыток. Если ни один кадр не проходит порог,
    возвращается тот, у которого наибольшее значение дисперсии.
    """
    attempts = 0
    best_variance = 0
    best_frame = None
    best_index = None
    attempted_indices = set()
    frame_range = end_frame - start_frame

    while attempts < max_attempts and len(attempted_indices) < frame_range:
        random_index = random.randint(start_frame, end_frame - 1)
        if random_index in attempted_indices:
            continue
        attempted_indices.add(random_index)
        cap.set(cv2.CAP_PROP_POS_FRAMES, random_index)
        ret, frame = cap.read()
        if not ret:
            continue
        is_sharp, var = is_sharp_frame(frame, threshold)
        if is_sharp:
            return frame, random_index, var
        if var > best_variance:
            best_variance = var
            best_frame = frame
            best_index = random_index
        attempts += 1

    # Если ни один кадр не удовлетворил порог, возвращаем лучший найденный вариант
    return best_frame, best_index, best_variance

def get_sharp_frames_from_video(video_path = 'upload/10.mp4'):
    # Основной блок
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Ошибка открытия видео файла.")
        exit()

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Всего кадров:", frame_count)

    # Делим видео на три равные части
    section_size = frame_count // 3
    results = {}
    threshold = 100    # Порог для определения резкости
    max_attempts = 20  # Максимальное число попыток поиска в каждой части

    for i in range(3):
        start = i * section_size
        # Для первых двух частей - фиксированный размер, для третьей - до конца файла
        end = (i + 1) * section_size if i < 2 else frame_count
        frame, index, var = get_random_sharp_frame(cap, start, end, threshold, max_attempts)
        if frame is not None:
            results[f'part_{i+1}'] = {'frame': frame, 'index': index, 'variance': var}
            print(f"Часть {i+1}: найден кадр с индексом {index}, дисперсия = {var:.2f}")
        else:
            print(f"Часть {i+1}: не найден чёткий кадр.")

    cap.release()
    # print(results.items())
    return [x[1]['frame'] for x in results.items()]


if __name__ == "__main__":
    f1, f2, f3 = get_sharp_frames_from_video()
    cv2.imshow("1",f1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imshow("1",f2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imshow("1",f3)
    cv2.waitKey(0)
    cv2.destroyAllWindows()