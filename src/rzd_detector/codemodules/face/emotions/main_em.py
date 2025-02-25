import cv2
import matplotlib.pyplot as plt
import numpy as np
from keras.preprocessing import image

from collections import Counter
from tqdm import tqdm

def load_image(image_path, grayscale=False, target_size=None):
    pil_image = image.load_img(image_path, grayscale, target_size)
    return image.img_to_array(pil_image)

def load_detection_model(model_path):
    detection_model = cv2.CascadeClassifier(model_path)
    return detection_model

def detect_faces(detection_model, gray_image_array):
    return detection_model.detectMultiScale(gray_image_array, 1.3, 5)

def apply_offsets(face_coordinates, offsets):
    x, y, width, height = face_coordinates
    x_off, y_off = offsets
    return (x - x_off, x + width + x_off, y - y_off, y + height + y_off)

def get_colors(num_classes):
    colors = plt.cm.hsv(np.linspace(0, 1, num_classes)).tolist()
    plt.close()
    colors = np.asarray(colors) * 255
    return colors

import numpy as np
from cv2 import imread
import cv2


def preprocess_input(x, v2=True):
    x = x.astype('float32')
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x


def _imread(image_name):
      i = imread(image_name)
      i = cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
      return i


def _imresize(image_array, size):
      return cv2.resize(image_array, dsize=size, interpolation=cv2.INTER_CUBIC)


def to_categorical(integer_classes, num_classes=2):
    integer_classes = np.asarray(integer_classes, dtype='int')
    num_samples = integer_classes.shape[0]
    categorical = np.zeros((num_samples, num_classes))
    categorical[np.arange(num_samples), integer_classes] = 1
    return categorical

from statistics import mode

import cv2
from keras.models import load_model
import numpy as np

# parameters for loading data and images
emotion_model_path = './fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy',
                4: 'sad', 5: 'surprise', 6: 'neutral'}

# hyper-parameters for bounding boxes shape
frame_window = 30
emotion_offsets = (20, 40)

# loading models
face_detection = load_detection_model("haarcascade_frontalface_default.xml")
emotion_classifier = load_model(emotion_model_path, compile=False)

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

# starting lists for calculating modes
emotion_window = []

# starting video streaming
def get_emotion(path):
    video_capture = cv2.VideoCapture(path)
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    count = 0
    emotions = []
    for i in tqdm(range(frame_count)):
        if count != 5:
            count += 1
            continue
        else:
            count = 1

        succes, bgr_image = video_capture.read()
        gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        faces = detect_faces(face_detection, gray_image)

        for face_coordinates in faces:
            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]
            try:
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except:
                continue

            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            emotion_prediction = emotion_classifier.predict(gray_face, verbose=0)
            emotion_probability = np.max(emotion_prediction)
            emotion_label_arg = np.argmax(emotion_prediction)
            emotion_text = emotion_labels[emotion_label_arg]
            emotions.append(emotion_text)
            # print(emotion_window)
    rel = dict(Counter(emotions))
    
    return [{x:(rel[x] / sum(rel.values()))} for x in rel]
