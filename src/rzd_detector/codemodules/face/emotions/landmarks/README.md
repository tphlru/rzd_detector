# Модуль `landmarks.py`

Этот модуль предназначен для обработки изображений лиц и извлечения координат лицевых ориентиров (landmarks) с использованием библиотеки `mediapipe`. Он предоставляет класс `FaceLandmarksProcessor` для обнаружения лиц на изображениях, извлечения координат ориентиров и выполнения различных операций, таких как скрытие глаз/рта и криволинейная обрезка.

## Обзор

Модуль состоит из двух основных классов:

-   `FaceLandmarksProcessor`: Основной класс для обработки изображений и извлечения лицевых ориентиров.
-   `FaceLandmarksResult`: Класс, содержащий результаты обработки, включая исходное изображение, обработанное изображение, координаты ориентиров и маску лица.

## Класс `FaceLandmarksProcessor`

### Инициализация

Для начала работы с модулем необходимо создать экземпляр класса `FaceLandmarksProcessor`.

```python
from rzd_detector.codemodules.face.emotions.landmarks import FaceLandmarksProcessor

processor = FaceLandmarksProcessor(verbose=False)
```

-   `verbose`: (bool, optional) Если `True`, будут отображаться отладочные изображения. По умолчанию `False`.

### Метод `process_landmarks`

Этот метод является основным для обработки изображений. Он принимает путь к изображению или изображение в формате `numpy.ndarray`, обнаруживает лицевые ориентиры и применяет опциональные модификации.

```python
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
) -> "FaceLandmarksResult":
```

**Аргументы:**

-   `image` (Union[str, numpy.ndarray]): Путь к изображению или изображение в формате OpenCV.
-   `save_path` (str, optional): Путь для сохранения обработанного изображения. Если указан, изображение будет сохранено.
-   `hide_eyes` (bool, optional): Скрывать ли области глаз. По умолчанию `True`.
-   `hide_mouth` (bool, optional): Скрывать ли область рта. По умолчанию `True`.
-   `mouth_k` (float, optional): Коэффициент для закрытия губ (0-1 и больше). По умолчанию `0.5`.
-   `curve_crop` (bool, optional): Применять ли криволинейную обрезку лица. По умолчанию `True`.
-   `return_image` (bool, optional): Возвращать ли обработанное изображение вместе с маркерами. По умолчанию `False`.
-   `return_raw` (bool, optional): Возвращать ли landmarks в необработанном виде. По умолчанию `False`.

**Возвращает:**

-   `FaceLandmarksResult`: Объект, содержащий результаты обработки. Возвращает `None`, если лицо не обнаружено.

**Пример использования:**

```python
image_path = "path/to/your/image.jpg"
result = processor.process_landmarks(
	image_path,
	save_path="path/to/save/processed_image.jpg",
	hide_eyes=True,
	hide_mouth=True,
	curve_crop=True,
	return_image=True,
)

if result:
	processed_image = result.processed_image  # Получаем обработанное изображение
	# Дальнейшая работа с изображением
else:
	print("Лицо не обнаружено")
```

## Класс `FaceLandmarksResult`

Этот класс предназначен для хранения результатов обработки изображения.

### Атрибуты

-   `original_image` (numpy.ndarray): Исходное изображение.
-   `landmarks` (numpy.ndarray): Координаты маркеров лица.
-   `processed_image` (numpy.ndarray): Обработанное изображение (доступно, если `return_image=True` в `process_landmarks`).
-   `raw` (numpy.ndarray): Необработанные координаты маркеров лица (None если `return_raw=False` в `process_landmarks`).
-   `last_crop_info` (dict): Информация об обрезке лица, используемая для восстановления координат на полном изображении.

### Методы

#### `get_full_mask()`

Возвращает маску исходного изображения, где область лица выделена белым цветом. Маска вычисляется с использованием сохраненных координат обрезки.

```python
def get_full_mask(self):
```

**Возвращает:**

-   `numpy.ndarray`: Маска лица на исходном изображении. Возвращает `None`, если информация об обрезке отсутствует.

**Пример использования:**

```python
full_mask = result.get_full_mask()
if full_mask is not None:
	# Дальнейшая работа с маской
	pass
```

#### `save_image(path)`

Сохраняет обработанное изображение по указанному пути.

```python
def save_image(self, path):
```

**Аргументы:**

-   `path` (str): Путь для сохранения изображения.

**Пример использования:**

```python
result.save_image("path/to/save/processed_image.jpg")
```

## Примеры использования

### Пример 1: Обработка изображения и получение координат

```python
import cv2
from rzd_detector.codemodules.face.emotions.landmarks import FaceLandmarksProcessor

# Инициализация процессора
processor = FaceLandmarksProcessor()

# Путь к изображению
image_path = "path/to/your/image.jpg"

# Обработка изображения
result = processor.process_landmarks(image_path, return_image=True)

# Проверка, что лицо было обнаружено
if result:
	# Получение координат лицевых ориентиров
	landmarks = result.landmarks

	# Вывод координат
	for i, (x, y, z) in enumerate(landmarks):
		print(f"Landmark {i}: x={x:.4f}, y={y:.4f}, z={z:.4f}")

	# Отображение обработанного изображения
	cv2.imshow("Processed Image", result.processed_image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
else:
	print("Лицо не обнаружено.")
```

### Пример 2: Скрытие глаз и рта, криволинейная обрезка

```python
import cv2
from rzd_detector.codemodules.face.emotions.landmarks import FaceLandmarksProcessor

# Инициализация процессора
processor = FaceLandmarksProcessor()

# Путь к изображению
image_path = "path/to/your/image.jpg"

# Обработка изображения с опциями
result = processor.process_landmarks(
	image_path, hide_eyes=True, hide_mouth=True, curve_crop=True, return_image=True
)

# Проверка, что лицо было обнаружено
if result:
	# Отображение обработанного изображения
	cv2.imshow("Processed Image", result.processed_image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
else:
	print("Лицо не обнаружено.")
```

### Пример 3: Получение маски лица на полном изображении

```python
import cv2
from rzd_detector.codemodules.face.emotions.landmarks import FaceLandmarksProcessor

# Инициализация процессора
processor = FaceLandmarksProcessor()

# Путь к изображению
image_path = "path/to/your/image.jpg"

# Обработка изображения
result = processor.process_landmarks(image_path, return_image=True)

# Проверка, что лицо было обнаружено
if result:
	# Получение маски лица
	full_mask = result.get_full_mask()

	# Отображение маски
	cv2.imshow("Full Mask", full_mask)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
else:
	print("Лицо не обнаружено.")
```

## Дополнительная информация

-   Для работы с модулем необходимо установить библиотеку `mediapipe`.
-   Координаты лицевых ориентиров нормализованы в диапазоне [0, 1].
-   Параметр `mouth_k` позволяет регулировать степень закрытия рта при применении маски.

Этот модуль предоставляет удобный и гибкий способ для обработки изображений лиц и извлечения лицевых ориентиров с возможностью применения различных модификаций.