import cv2
import requests
import numpy as np

url = 'http://tphl.duckdns.org/video_feed'

stream = requests.get(url, stream=True)

# Переменная для хранения байтового контента
byte_buffer = bytes()

# Чтение кадров из потока
for chunk in stream.iter_content(chunk_size=1024):
    byte_buffer += chunk

    # Поиск начала и конца кадра (JPEG изображения)
    start_index = byte_buffer.find(b'\xff\xd8')  # Начало JPEG
    end_index = byte_buffer.find(b'\xff\xd9')    # Конец JPEG

    # Если нашли полный JPEG кадр
    if start_index != -1 and end_index != -1:
        jpg_frame = byte_buffer[start_index:end_index+2]
        byte_buffer = byte_buffer[end_index+2:]

        # Преобразование байтов в изображение
        image = cv2.imdecode(np.frombuffer(jpg_frame, dtype=np.uint8), cv2.IMREAD_COLOR)

        # Отображение кадра
        cv2.imshow('MJPEG Stream', image)

        # Выход при нажатии клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Закрытие всех окон OpenCV
cv2.destroyAllWindows()
