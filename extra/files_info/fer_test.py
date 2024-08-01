from fer import FER
emo_detector = FER(mtcnn=True)
import matplotlib.pyplot as plt

test_image_one = plt.imread("/emo/test_img1.jpg")

captured_emotions = emo_detector.detect_emotions(test_image_one)

print(captured_emotions)
plt.imshow(test_image_one)

dominant_emotion, emotion_score = emo_detector.top_emotion(test_image_one)
print(dominant_emotion, emotion_score)
