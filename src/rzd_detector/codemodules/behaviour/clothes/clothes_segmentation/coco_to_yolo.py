from ultralytics.data.converter import convert_coco
import cv2
from glob import glob
from tqdm import tqdm
import shutil

# convert_coco(labels_dir=r"C:\Users\Georges\Projects\datasets\DeepFashion2\train\annotations", save_dir=r"C:\Users\Georges\Projects\datasets\DeepFashion2\train\yolo")
# convert_coco(labels_dir=r"C:\Users\Georges\Projects\datasets\DeepFashion2\validation\annotations", save_dir=r"C:\Users\Georges\Projects\datasets\DeepFashion2\validation\yolo")
# convert_coco(labels_dir=r"C:\Users\Georges\Projects\datasets\DeepFashion2\test\annotations", save_dir=r"C:\Users\Georges\Projects\datasets\DeepFashion2\test\yolo")


training_images = glob(r"C:\Users\Georges\Projects\datasets\DeepFashion2\train\image\*.*")
validation_images = glob(r"C:\Users\Georges\Projects\datasets\DeepFashion2\validation\image\*.*")

test_images = training_images + validation_images
test_images = test_images[0:int((len(training_images) + len(validation_images))*0.2)]
training_images = [x for x in tqdm(training_images) if x not in test_images]
validation_images = [x for x in tqdm(validation_images) if x not in test_images]
print(len(test_images), len(training_images) + len(validation_images))
for name in tqdm(training_images):
    shutil.move(name, r"C:\Users\Georges\Projects\datasets\DeepFashion2_Coco\images\train\\" + name.split("\\")[-1])
for name in tqdm(validation_images):
    shutil.move(name, r"C:\Users\Georges\Projects\datasets\DeepFashion2_Coco\images\validation" + name.split("\\")[-1])
for name in tqdm(test_images):
    shutil.move(name, r"C:\Users\Georges\Projects\datasets\DeepFashion2_Coco\images\test" + name.split("\\")[-1])