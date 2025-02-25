class DepthEstimator:
    """Класс DepthEstimator для генерации карт глубин из изображений.

    Этот класс предоставляет методы для загрузки изображений, генерации карт глубин,
    сохранения результатов и возврата карты глубин в виде 16-битного массива.
    Также позволяет выбирать между использованием GPU и CPU для обработки.
    """

    def __init__(self, use_gpu=True):
        """Инициализация класса DepthEstimator, предзагрузка библиотек и моделей.

        Args:
            use_gpu (bool): Если True, используется GPU для обработки, иначе CPU.
        """
        self.use_gpu = use_gpu
        self.pipe = None
        self._load_model()

    def _load_model(self):
        """Предзагрузка необходимых библиотек и моделей для генерации карт глубин."""
        from diffusers import DiffusionPipeline
        import torch

        self.pipe = DiffusionPipeline.from_pretrained(
            "GonzaloMG/marigold-e2e-ft-depth",
            custom_pipeline="GonzaloMG/marigold-e2e-ft-depth",
            torch_dtype=torch.float16 if self.use_gpu else torch.float32,
        ).to("cuda" if self.use_gpu else "cpu")

    def _load_image(self, image_input):
        """Загрузка изображения из файла или OpenCV (преобразование в RGB).

        Args:
            image_input (str или numpy.ndarray): Путь к файлу изображения или изображение в формате OpenCV.

        Returns:
            загруженное изображение
        """
        import numpy as np
        import os
        import cv2

        if isinstance(image_input, str):
            if not os.path.isfile(image_input):
                raise FileNotFoundError(f"Файл не найден: {image_input}")
            image = cv2.imread(image_input)
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif isinstance(image_input, np.ndarray):
            return cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError(
                "Входные данные должны быть строкой (путь к файлу) или массивом NumPy."
            )

    def _generate(self, image):
        return self.pipe(image=image)

    def _save_depth_map_img(self, depth, output_path):
        """Сохранение карты глубин в 16-битном формате PNG.

        Args:
            depth: карта глубин
            output_path (str): путь для сохранения результата
        """

        depth_image = self.pipe.image_processor.export_depth_to_16bit_png(
            depth.prediction
        )[0]
        depth_image.save(output_path)

    def _reshape_depth_map(self, depthmap):
        """Преобразование карты глубин в 3-мерный массив.

        Args:
            depthmap: карта глубин

        Returns:
            3-мерный массив карты глубин
        """
        return depthmap.squeeze()

    def show_heatmap(self, depthmap):
        """Отображение карты глубин в виде тепловой карты.

        Args:
            depthmap: карта глубин
        """
        import matplotlib.pyplot as plt

        depthmap = depthmap.squeeze()
        # invert heatmap for better visualization
        depthmap = 1 - depthmap
        plt.imshow(depthmap, cmap="gray")
        # possible cmaps: 'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'gray'
        plt.axis("off")
        plt.show()
        plt.close()

    def infer(self, image_input, save_path=None, fix_shape=True):
        """Генерация карты глубин из изображения.

        Args:
            image_input (str или numpy.ndarray): Путь к файлу изображения или изображение в формате OpenCV.
            save_path (str, optional): Путь для сохранения результата. Если указан, карта глубин будет сохранена в
                формате PNG. По умолчанию None.
            fix_shape (bool, optional): Если True, возвращает карту глубин в виде 3-мерного массива, иначе возвращает
                исходную форму. По умолчанию True.

        Returns:
            numpy.ndarray: Карта глубин.
        """
        image = self._load_image(image_input)
        depth = self._generate(image)
        if save_path:
            self._save_depth_map_img(depth, save_path)
        pred = depth.prediction
        return self._reshape_depth_map(pred) if fix_shape else pred
