# from diffusers import DiffusionPipeline
# import diffusers
# import torch

# image = diffusers.utils.load_image(
#     "https://gonzalomartingarcia.github.io/diffusion-e2e-ft/static/lego.jpg"
# )

# # Depth
# pipe = DiffusionPipeline.from_pretrained(
#     "GonzaloMG/marigold-e2e-ft-depth",
#     custom_pipeline="GonzaloMG/marigold-e2e-ft-depth",
#     torch_dtype=torch.float16,  # Оптимизация памяти
# ).to("cuda")

# # Явно указываем, что вход — изображение
# depth = pipe(image=image)

# # Сохраняем результаты
# pipe.image_processor.export_depth_to_16bit_png(depth.prediction)[0].save(
#     "depth_16bit.png"
# )

# from rzd_detector.codemodules.face.emotions.depth_estimation.depth_estimator import (
#     DepthEstimator,
# )

# print("Инициализация класса DepthEstimator")
# estimator = DepthEstimator(use_gpu=True)
# print("Обработка изображения")
# d = estimator.infer(
#     "/home/timur/Download/lego.jpg", "/home/timur/Download/lego_depth.png"
# )
# print("done 1")
# estimator.show_heatmap(d)

import cv2
from rzd_detector.codemodules.face.emotions.depth_estimation import DepthEstimator

# Инициализация класса DepthEstimator
depth_estimator = DepthEstimator(use_gpu=True)

# Загрузка изображения с использованием OpenCV
image = cv2.imread(
    "src/rzd_detector/codemodules/face/emotions/dev/sample_imgs/face.jpg"
)

# Генерация карты глубин из изображения OpenCV и сохранение результата
save_path = "src/rzd_detector/codemodules/face/emotions/dev/depth_map.png"
depth_map = depth_estimator.infer(image, save_path=save_path)

# Вывод формы карты глубин
print(depth_map.shape)
