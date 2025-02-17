# Модуль Depth Estimator

Этот модуль предоставляет класс `DepthEstimator` для генерации карт глубин из изображений. Он использует предварительно обученную модель для оценки глубины и предоставляет методы для загрузки изображений, генерации карт глубин, сохранения результатов и отображения карт глубин.

## Объекты класса `DepthEstimator`

*   `use_gpu` (bool): Определяет, использовать ли GPU для обработки. По умолчанию `True`.
*   `pipe`: Объект пайплайна Diffusers, используемый для генерации карт глубин. Инициализируется в методе `_load_model`.

## Методы класса

*   `__init__(self, use_gpu=True)`: Инициализирует класс `DepthEstimator`, предзагружает библиотеки и модели.
	*   `use_gpu` (bool): Если `True`, используется GPU для обработки, иначе CPU.
*   `infer(self, image_input, save_path=None, fix_shape=True)`: Генерирует карту глубин из изображения.
	*   `image_input` (str или numpy.ndarray): Путь к файлу изображения или изображение в формате OpenCV.
	*   `save_path` (str, optional): Путь для сохранения результата. Если указан, карта глубин будет сохранена в формате PNG. По умолчанию `None`.
	*   `fix_shape` (bool, optional): Если `True`, возвращает карту глубин в виде 3-мерного массива, иначе возвращает исходную форму. По умолчанию `True`.
*   `show_heatmap(self, depthmap)`: Отображает карту глубин в виде тепловой карты.
	*   `depthmap`: Карта глубин.

## Выходной формат

Метод `infer` возвращает карту глубин в виде массива NumPy. Если `fix_shape=True` (рекомендуется), то возвращается 3-мерный массив. Если `fix_shape=False`, то возвращается исходная форма, сгенерированная моделью.

## Примеры использования

### 1. Инициализация класса и генерация карты глубин из файла

```python
from rzd_detector.codemodules.face.emotions.depth_estimation import DepthEstimator

# Инициализация класса DepthEstimator с использованием GPU
depth_estimator = DepthEstimator(use_gpu=True)

# Генерация карты глубин из файла
image_path = "path/to/your/image.jpg"
depth_map = depth_estimator.infer(image_path)

# Вывод формы карты глубин
print(depth_map.shape)
```

### 2. Генерация карты глубин из изображения OpenCV и сохранение результата

```python
import cv2
from rzd_detector.codemodules.face.emotions.depth_estimation import DepthEstimator

# Инициализация класса DepthEstimator с использованием CPU
depth_estimator = DepthEstimator(use_gpu=False)

# Загрузка изображения с использованием OpenCV
image = cv2.imread("path/to/your/image.jpg")

# Генерация карты глубин из изображения OpenCV и сохранение результата
save_path = "path/to/save/depth_map.png"
depth_map = depth_estimator.infer(image, save_path=save_path)

# Вывод формы карты глубин
print(depth_map.shape)
```

### 3. Отображение карты глубин в виде тепловой карты

```python
import cv2
from rzd_detector.codemodules.face.emotions.depth_estimation import DepthEstimator

# Инициализация класса DepthEstimator
depth_estimator = DepthEstimator()

# Загрузка изображения с использованием OpenCV
image = cv2.imread("path/to/your/image.jpg")

# Генерация карты глубин
depth_map = depth_estimator.infer(image)

# Отображение карты глубин в виде тепловой карты
depth_estimator.show_heatmap(depth_map)
```