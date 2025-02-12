from diffusers import DiffusionPipeline
import diffusers
import torch

image = diffusers.utils.load_image("/home/timur/Download/test2.jpg")

# Depth
pipe = DiffusionPipeline.from_pretrained(
    "GonzaloMG/marigold-e2e-ft-depth",
    custom_pipeline="GonzaloMG/marigold-e2e-ft-depth",
    torch_dtype=torch.float16,  # Оптимизация памяти
).to("cuda")

# Явно указываем, что вход — изображение
depth = pipe(image=image)

# Сохраняем результаты
pipe.image_processor.export_depth_to_16bit_png(depth.prediction)[0].save(
    "depth_16bit.png"
)
