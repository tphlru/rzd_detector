## Функция `process_landmarks`

Функция `process_landmarks` является основной функцией для обработки изображений лиц. Она принимает изображение, обнаруживает лицевые маркеры и применяет различные модификации, такие как скрытие глаз и рта, а также криволинейную обрезку лица.

**Аргументы:**

*   `image` (Union[str, numpy.ndarray]): Путь к изображению или изображение в формате OpenCV (массив numpy).
*   `save_path` (Optional[str]): Путь для сохранения обработанного изображения. Если не указан, изображение не сохраняется.
*   `hide_eyes` (bool): Флаг, указывающий, нужно ли скрывать области глаз. По умолчанию `True`.
*   `hide_mouth` (bool): Флаг, указывающий, нужно ли скрывать область рта. По умолчанию `True`.
*   `curve_crop` (bool): Флаг, указывающий, нужно ли применять криволинейную обрезку лица. По умолчанию `True`.
*   `return_image` (bool): Флаг, указывающий, нужно ли возвращать обработанное изображение вместе с маркерами. По умолчанию `False`.
*   `verbose` (bool): Флаг, указывающий, нужно ли отображать результирующее изображение с помощью `cv2.imshow`. По умолчанию `False`.

**Возвращаемое значение:**

*   Если `return_image=True`: Возвращает кортеж `(landmarks, result_image)`, где `landmarks` - это список координат лицевых маркеров, а `result_image` - обработанное изображение.
*   Если `return_image=False`: Возвращает список координат лицевых маркеров `landmarks`.
*   Если лицо не обнаружено: Возвращает `None`.

**Исключения:**

*   `FileNotFoundError`: Если `image` является строкой (путем к файлу), и файл не найден.
*   `ValueError`: Если `image` не является ни строкой, ни массивом numpy.

**Примеры использования:**

1.  **Простая обработка изображения с сохранением результата:**

	```python
	from rzd_detector.codemodules.face.emotions.landmarks import process_landmarks

	image_path = "path/to/your/image.jpg"
	save_path = "path/to/save/processed_image.jpg"
	landmarks = process_landmarks(image_path, save_path=save_path)

	if landmarks:
		print(f"Обнаружено {len(landmarks)} маркеров лица.")
	else:
		print("Лицо не обнаружено.")
	```

	В этом примере изображение по указанному пути обрабатывается, лицевые маркеры обнаруживаются, и результат сохраняется в указанный файл.  Глаза и рот скрываются, и применяется криволинейная обрезка по умолчанию.

2.  **Обработка изображения с возвратом маркеров и изображения:**

	```python
	from rzd_detector.codemodules.face.emotions.landmarks import process_landmarks
	import cv2

	image_path = "path/to/your/image.jpg"
	landmarks, processed_image = process_landmarks(image_path, return_image=True)

	if landmarks:
		print(f"Обнаружено {len(landmarks)} маркеров лица.")
		cv2.imshow("Processed Image", processed_image)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
	else:
		print("Лицо не обнаружено.")
	```

	В этом примере изображение обрабатывается, и возвращаются как маркеры лица, так и обработанное изображение.  Обработанное изображение отображается с использованием `cv2.imshow`.

3.  **Обработка изображения без скрытия глаз и рта, без криволинейной обрезки:**

	```python
	from rzd_detector.codemodules.face.emotions.landmarks import process_landmarks

	image_path = "path/to/your/image.jpg"
	landmarks = process_landmarks(image_path, hide_eyes=False, hide_mouth=False, curve_crop=False)

	if landmarks:
		print(f"Обнаружено {len(landmarks)} маркеров лица.")
	else:
		print("Лицо не обнаружено.")
	```

	В этом примере обработка выполняется без скрытия глаз и рта, а также без криволинейной обрезки.

4.  **Обработка изображения из массива numpy:**

	```python
	from rzd_detector.codemodules.face.emotions.landmarks import process_landmarks
	import cv2

	image = cv2.imread("path/to/your/image.jpg")
	landmarks = process_landmarks(image)

	if landmarks:
		print(f"Обнаружено {len(landmarks)} маркеров лица.")
	else:
		print("Лицо не обнаружено.")
	```

	В этом примере изображение загружается в формате numpy array с помощью `cv2.imread`, а затем передается в функцию `process_landmarks`.

5. **Отображение результирующего изображения в процессе обработки:**

	```python
	from rzd_detector.codemodules.face.emotions.landmarks import process_landmarks

	image_path = "path/to/your/image.jpg"
	landmarks = process_landmarks(image_path, verbose=True)

	if landmarks:
		print(f"Обнаружено {len(landmarks)} маркеров лица.")
	else:
		print("Лицо не обнаружено.")
	```

	В этом примере, установив `verbose=True`, результирующее изображение будет отображено с использованием `cv2.imshow` в процессе обработки. Это полезно для отладки и визуальной оценки результатов.