# Наша модель распознования эмоций по интонации голоса

import logging
import os

import numpy as np
from tensorflow.keras.models import load_model
import pickle
import librosa

logger = logging.getLogger(__name__)


def _extract_features(data, sample_rate):
    # ZCR
    result = np.array([])
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=data).T, axis=0)
    result = np.hstack((result, zcr))  # Добавляем

    # Chroma_stft
    stft = np.abs(librosa.stft(data))
    chroma_stft = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
    result = np.hstack((result, chroma_stft))  # Добавляем

    # MFCC
    mfcc = np.mean(librosa.feature.mfcc(y=data, sr=sample_rate).T, axis=0)
    result = np.hstack((result, mfcc))  # Добавляем

    # Root Mean Square Value
    rms = np.mean(librosa.feature.rms(y=data).T, axis=0)
    result = np.hstack((result, rms))  # Добавляем

    # MelSpectogram
    mel = np.mean(librosa.feature.melspectrogram(y=data, sr=sample_rate).T, axis=0)
    result = np.hstack((result, mel))  # Добавляем

    return result


def _get_predict_feat(path, scaler):
    d, sample_rate = librosa.load(path, offset=0.5)
    res = _extract_features(d, sample_rate)
    result = np.array(res)
    result = np.reshape(result, newshape=(1, 162))
    i_result = scaler.transform(result)
    return np.expand_dims(i_result, axis=2)


def load_simple_model(modeldir="models/posneg/"):
    """Загрузить нашу обученную модель бинарного (позитивная / негативная) определения эмоций.

    Args:
        modeldir (str, optional): Путь к директории с моделью (model.keras), scaler.pickle и encoder.pickle
            по умолчанию "models/posneg/"

    Returns:
        tuple: (loaded_model, scaler, encoder)
    """
    # Загружаем нашу модель, обученнуюю нами в блокноте
    loaded_model = load_model(os.path.join(modeldir, "model.keras"))
    # Загружаем scaler и энкодер из сохранённых объектов
    with open(os.path.join(modeldir, "scaler.pickle"), "rb") as f:
        scaler = pickle.load(f)
    with open(os.path.join(modeldir, "encoder.pickle"), "rb") as f:
        encoder = pickle.load(f)
    logger.info("Модель бинарного определения эмоций загружена успешно")
    return loaded_model, scaler, encoder


def detect_intonation_simple(path: str, loaded_model, scaler, encoder):
    """Определить эмоцию интонации речи в аудиофайле. Использует нашу обученную модель позитивное / негативное.

    Args:
        path (str): Путь к аудиофайлу, только речь. Рекомендуемая длительность 3-5 секунд.
        loaded_model (keras.model): Загруженная модель бинарного определения эмоций
        scaler (sklearn.preprocessing): Скалер
        encoder (sklearn.preprocessing): Энкодер

    Returns:
        bool: True - позитивная эмоция, False - негативная
    """

    features = _get_predict_feat(path, scaler)
    predictions = loaded_model.predict(features)
    y_pred = encoder.inverse_transform(predictions)
    return {"bad": False, "good": True}.get(y_pred[0][0])
