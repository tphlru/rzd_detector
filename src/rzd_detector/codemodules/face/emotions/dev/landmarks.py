# import cv2
# import mediapipe as mp
# import numpy as np

# img = cv2.imread("/home/timur/Download/test4.jpg")
# if img is None:
#     print("Изображение не найдено!")
#     exit()
# h, w, _ = img.shape

# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(
#     static_image_mode=True,
#     max_num_faces=1,
#     refine_landmarks=True,
#     min_detection_confidence=0.5,
# )
# rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# results = face_mesh.process(rgb)
# face_mesh.close()


# # Извлечение landmarks (для первого найденного лица)
# landmarks = results.multi_face_landmarks[0].landmark
# points = []
# points.extend((lm.x * w, lm.y * h, lm.z) for lm in landmarks)
# points_np = np.array(points)

# # bounding box лица
# xs = points_np[:, 0]
# ys = points_np[:, 1]
# min_x = int(np.min(xs))
# min_y = int(np.min(ys))
# max_x = int(np.max(xs))
# max_y = int(np.max(ys))

# face_crop = img[min_y:max_y, min_x:max_x]

# # Преобразовываем координаты landmarks в локальные координаты относительно face_crop
# local_landmarks = []
# local_landmarks.extend((pt[0] - min_x, pt[1] - min_y, pt[2]) for pt in points)
# local_landmarks = np.array(local_landmarks)

# left_eye_ids = [
#     33,
#     7,
#     163,
#     144,
#     145,
#     153,
#     154,
#     155,
#     133,
#     173,
#     157,
#     158,
#     159,
#     160,
#     161,
#     246,
# ]
# right_eye_ids = [
#     263,
#     249,
#     390,
#     373,
#     374,
#     380,
#     381,
#     382,
#     362,
#     398,
#     384,
#     385,
#     386,
#     387,
#     388,
#     466,
# ]
# mouth_ids = [
#     78,
#     95,
#     88,
#     178,
#     87,
#     14,
#     317,
#     402,
#     318,
#     324,
#     308,
#     415,
#     310,
#     311,
#     312,
#     13,
#     82,
# ]

# # Создаем пустую маску размером с лицо
# mask = np.zeros(face_crop.shape[:2], dtype=np.uint8)

# # Создаем полигон для левого глаза
# left_eye_poly = []
# for i in left_eye_ids:
#     x, y, _ = local_landmarks[i]
#     left_eye_poly.append([int(x), int(y)])
# left_eye_poly = np.array(left_eye_poly, np.int32)

# # Создаем полигон для правого глаза
# right_eye_poly = []
# for i in right_eye_ids:
#     x, y, _ = local_landmarks[i]
#     right_eye_poly.append([int(x), int(y)])
# right_eye_poly = np.array(right_eye_poly, np.int32)

# # Создаем полигон для рта
# mouth_poly = []
# for i in mouth_ids:
#     x, y, _ = local_landmarks[i]
#     mouth_poly.append([int(x), int(y)])
# mouth_poly = np.array(mouth_poly, np.int32)

# # Заполняем маску полигонами глаз и рта (значение 255)
# cv2.fillPoly(mask, [left_eye_poly], 255)
# cv2.fillPoly(mask, [right_eye_poly], 255)
# cv2.fillPoly(mask, [mouth_poly], 255)

# # Создаем полигон для контура лица (крайние по координатам точки - convexHull)
# local_points = local_landmarks[:, :2].astype(np.int32)
# face_contour_poly = cv2.convexHull(local_points)

# face_mask = np.zeros(face_crop.shape[:2], dtype=np.uint8)
# cv2.fillPoly(face_mask, [face_contour_poly], 255)

# # Создаем изображение с белым фоном
# face_with_white_bg = face_crop.copy()
# face_with_white_bg[face_mask == 0] = (255, 255, 255)


# # Применяем инвертированную маску к изображению с белым фоном
# full_masked_white_bg_image = cv2.bitwise_and(
#     face_with_white_bg, face_with_white_bg, mask=cv2.bitwise_not(mask)
# )

# # Области, где была маска, должны быть белыми, а не черными
# full_masked_white_bg_image[mask == 255] = (255, 255, 255)

# cv2.imshow("x", full_masked_white_bg_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

from rzd_detector.codemodules.face.emotions.landmarks import process_landmarks

i = process_landmarks(
    "/home/timur/Download/test4.jpg", hide_eyes=False, curve_crop=False, verbose=True
)
