# Depth Estimation 

### Импортирование класса

```python
from depth_estimator import DepthEstimator
```

### Создание экземпляра класса

```python
estimator = DepthEstimator(use_gpu=True)  # Установите use_gpu в False для использования CPU
```

### Генерация карты глубин

Вы можете загрузить изображение из файла или использовать OpenCV:

```python
# Загрузка из файла
depth_map = estimator.generate_depth_map("path/to/image.jpg")

# Загрузка через OpenCV
import cv2
image = cv2.imread("path/to/image.jpg")
depth_map = estimator.generate_depth_map(image)
```

### Сохранение

Вы можете сохранить результат на указанный путь:

```python
estimator.save_depth_map(depth_map, "path/to/save/depth_map.png")
```

Если вам нужно получить карту глубин в виде массива:

```python
depth_array = estimator.generate_depth_map("path/to/image.jpg", return_array=True)
```