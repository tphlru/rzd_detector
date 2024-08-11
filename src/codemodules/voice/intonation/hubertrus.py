import logging
import os

from transformers import HubertForSequenceClassification, Wav2Vec2FeatureExtractor
import torchaudio
import tensorflow as tf

# from tensorflow.keras.models import Sequential, model_from_json, load_model
# from tensorflow import device as tf_device
# import tensorflow as tf
# import pickle
# import librosa

# import pyaudio
# import sounddevice as sd
# import soundfile as sf
# import webrtcvad
# import numpy as np
# import time
# import queue

# from IPython.display import Audio
# from jupyterplot import ProgressPlot
# import timeit

logger = logging.getLogger(__name__)


def load_hubert_model(
    modeldir="models/hubert-rus/", force_reload=False, low_cpu_mem_usage=True
):
    """Загрузить модель hubert-rus с диска или huggingface hub

    Args:
        modeldir (str, optional): Путь к директории с файлами модели hubert. По умолчанию "models/hubert-rus/".
        force_reload (bool, optional): Принудительно загрузить модель из huggingface hub. По умолчанию False.
        low_cpu_mem_usage (bool, optional): Экономить использование RAM. По умолчанию True.

    Returns:
        tuple: (feature_extractor, model)
    """
    # Составим список путей для быстрой проверки
    paths = [
        "hubert-rus-feature-extractor",
        "hubert-rus-model",
        "hubert-rus-feature-extractor/preprocessor_config.json",
        "hubert-rus-model/config.json",
        "hubert-rus-model/model.safetensors",
    ]

    paths = [os.path.join(modeldir, path) for path in paths]

    if force_reload or not all(os.path.isfile(path) for path in paths[2:]):
        logger.info("Выполняется загрузка модели hubert-rus с hugging face hub...")
        # Загрузить модель hubert с hugging face hub и сохранить на диск
        feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
            "facebook/hubert-large-ls960-ft"
        )
        model = HubertForSequenceClassification.from_pretrained(
            "xbgoose/hubert-speech-emotion-recognition-russian-dusha-finetuned"
        )
        feature_extractor.save_pretrained(paths[0])
        model.save_pretrained(paths[1])
    else:
        # Загрузить модель hubert с диска
        feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
            os.path.abspath(paths[0]), low_cpu_mem_usage=low_cpu_mem_usage
        )
        model = HubertForSequenceClassification.from_pretrained(
            os.path.abspath(paths[1]), low_cpu_mem_usage=low_cpu_mem_usage
        )
    logger.info("Модель hubert-rus для определения эмоций загружена успешно!")
    return feature_extractor, model


def predict_hubert(filepath, feature_extractor, model):
    # Словарь, сопоставляющий номера с эмоциями
    num2emotion = {0: "neutral", 1: "angry", 2: "positive", 3: "sad", 4: "other"}
    # Загрузить аудиофайл
    waveform, sample_rate = torchaudio.load(filepath, normalize=True)
    # Преобразовать частоту дискретизации на стандартные 16000 Гц
    transform = torchaudio.transforms.Resample(sample_rate, 16000)
    waveform = transform(waveform)
    # Преобразовать аудиофайл в тензор с помощью feature_extractor
    inputs = feature_extractor(
        waveform,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True,
        max_length=16000 * 10,
        truncation=True,
    )
    # Выполнить предсказание и применить функцию активации softmax для получения вероятностей
    probabilities = (
        tf.nn.softmax(model(inputs["input_values"][0]).logits.detach(), axis=-1)
        .numpy()
        .tolist()[0]
    )
    # Преобразовать вероятности в словарь с текстовыми названиями эмоций
    probabilities = {num2emotion[n]: val for (n, val) in enumerate(probabilities)}
    # Вернуть отсортированный по убыванию словарь
    return dict(sorted(probabilities.items(), key=lambda x: x[1], reverse=True))
