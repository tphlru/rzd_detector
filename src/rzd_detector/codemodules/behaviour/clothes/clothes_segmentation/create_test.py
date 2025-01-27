from glob import glob
from tqdm import tqdm
import shutil
import os

standart_path = "/content/DeepFashion2_standart/"
train_path = standart_path + "train/"
validation_path = standart_path + "validation/"
test_path = standart_path + "test/"
print(test_path)

training = glob(train_path + r"image/*.*")
validation = glob(validation_path + r"image/*.*")
print(len(training) + len(validation))
test = training + validation
test_paths = test[0:int((len(training) + len(validation))*0.2)]
training = [x.split("/")[-1].replace(".jpg", "") for x in tqdm(training, desc="Sorting training", colour='green') if x not in test_paths]
validation = [x.split("/")[-1].replace(".jpg", "") for x in tqdm(validation, desc="Sorting validation", colour='green') if x not in test_paths]
print(f"Count  -  Train: {len(training)} Validation: {len(validation)} Test: {len(test)}")
test = [x.split("/")[-1].replace(".jpg", "") for x in tqdm(test, desc="Sorting test", colour='green')]

training_images = []
validation_images = []
test_images = []
training_annos = []
validation_annos = []
test_annos = []
for x in training:
    training_images.append(train_path + r"image/" + x + ".jpg")
    training_annos.append(train_path + r"annos/" + x + ".json")
for x in validation:
    validation_images.append(validation_path + r"image/" + x + ".jpg")
    validation_annos.append(validation_path + r"annos/" + x + ".json")
for x in test:
    test_images.append(test_path + r"image/" + x + ".jpg")
    test_annos.append(test_path + r"annos/" + x + ".json")

print(f"Count  -  Train: {len(training)} Validation: {len(validation)} Test: {len(test)}")
print(f"Images  -  Train: {training_images[0]} Validation: {validation_images[0]} Test: {test_images[0]}")
print(f"Annotations  -  Train: {training_annos[0]} Validation: {validation_annos[0]} Test: {test_annos[0]}")
os.mkdir("/content/DeepFashion2_standart/test")
os.mkdir("/content/DeepFashion2_standart/test/image")
os.mkdir("/content/DeepFashion2_standart/test/annos")
for img in tqdm(test_paths):
    annos = img.replace(".jpg", ".json").replace("image", "annos")
    test_images_path = test_path + 'image/'
    test_annos_path = test_path + 'annos/'
    shutil.move(img, test_images_path)
    shutil.move(annos, test_annos_path)