from glob import glob
import os
import shutil
from tqdm import tqdm
input_root_path = r"C:/Users/Georges/Projects/datasets/DeepFashion2_standart" # in stndrt DeepFashion format
output_root_path = r"C:/Users/Georges/Projects/datasets/DeepFashion2_10%" 
part = 10 # in %


def img_to_json(path: str):
    return path.replace("jpg", "json").replace("image", "annos")

def get_name(path: str):
    return path.split("\\")[-1]


def create_path(path):
    if not os.path.isdir(path):
        os.mkdir(path)

create_path(output_root_path)
create_path(input_root_path)
create_path(output_root_path + "/train")
create_path(output_root_path + "/test")
create_path(output_root_path + "/validation")
create_path(output_root_path + "/train/image")
create_path(output_root_path + "/test/image")
create_path(output_root_path + "/validation/image")
create_path(output_root_path + "/train/annos")
create_path(output_root_path + "/test/annos")
create_path(output_root_path + "/validation/annos")
train = glob(input_root_path + "/train/image/*.*")
test = glob(input_root_path + "/test/image/*.*")
validation = glob(input_root_path + "/validation/image/*.*")
# train
for i in tqdm(range(0, int(len(train)*(part/100))), desc="Train: "):
    shutil.copy(train[i].replace("\\", "/"), output_root_path + "/train/image/" + get_name(train[i]).replace("\\", "/"))
    shutil.copy(img_to_json(train[i].replace("\\", "/")), output_root_path + "/train/annos/" + get_name(train[i]).replace("jpg", "json").replace("\\", "/"))
#test
for i in tqdm(range(0, int(len(test)*(part/100))), desc="Test: "):
    shutil.copy(test[i].replace("\\", "/"), output_root_path + "/test/image/" + get_name(test[i]).replace("\\", "/"))
    shutil.copy(img_to_json(test[i].replace("\\", "/")), output_root_path + "/test/annos/" + get_name(test[i]).replace("jpg", "json").replace("\\", "/"))
#validation
for i in tqdm(range(0, int(len(validation)*(part/100))), desc="Validation: "):
    shutil.copy(validation[i].replace("\\", "/"), output_root_path + "/validation/image/" + get_name(validation[i]).replace("\\", "/"))
    shutil.copy(img_to_json(validation[i].replace("\\", "/")), output_root_path + "/validation/annos/" + get_name(validation[i]).replace("jpg", "json").replace("\\", "/"))
