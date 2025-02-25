from deepface import DeepFace

def detect_emotion(image):
    """Определяет эмоцию лица на изображении.

    Args:
        image_path (str): Путь к изображению.

    Returns:
        str: Название эмоции или сообщение об ошибке.
    """
    try:
        # Анализируем изображение с помощью DeepFace
        analysis = DeepFace.analyze(image, actions=['emotion'], enforce_detection=False)
        
        # Получаем наибольшую вероятность эмоции
        emotion = analysis[0]['dominant_emotion']
        return f"Определённая эмоция: {emotion}"

    except Exception as e:
        return f"Ошибка при анализе: {e}"

# Пример использования
image_path = "face.jpg"
print(detect_emotion(image_path))
