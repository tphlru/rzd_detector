import json
import cv2
from glob import glob
from tqdm import tqdm
import os.path
import yaml
standart_path = 'C:/Users/Georges/Projects/datasets/DeepFashion2_standart'
output_dir = 'C:/Users/Georges/Projects/datasets/DeepFashion2_YOLO'
data = {'path': output_dir,
        'train': output_dir + '/images/train',
        'val': output_dir + '/images/validation',
        'test': output_dir + '/images/test',
        'names': {
            0: 'lower',
            1: 'higher'
        }
}

with open(output_dir + "/data.yml", "w") as file:
    yaml.dump(data, file)

'''
----Input data structure----
standart_path
        |     
        |--train
        |   |
        |   |--annos
        |   |
        |   |--image
        |
        |--validation
        |   |
        |   |--annos
        |   |
        |   |--image
        |
        |--test
        |   |
        |   |--annos
        |   |
        |   |--image
        |
----------------------------
'''

'''
----Output data structur----
output_dir
        |     
        |--images
        |   |
        |   |--train
        |   |
        |   |--test
        |   |
        |   |--validation
        |
        |--labels
        |   |
        |   |--train
        |   |
        |   |--test
        |   |
        |   |--validation
----------------------------
'''
if not os.path.isdir(output_dir + '/images'):
    os.mkdir(output_dir + '/images')
if not os.path.isdir(output_dir + '/labels'):
    os.mkdir(output_dir + '/labels')
if not os.path.isdir(output_dir + '/images/train'):
    os.mkdir(output_dir + '/images/train')
if not os.path.isdir(output_dir + '/images/validation'):
    os.mkdir(output_dir + '/images/validation')
if not os.path.isdir(output_dir + '/images/test'):
    os.mkdir(output_dir + '/images/test')
if not os.path.isdir(output_dir + '/labels/train'):
    os.mkdir(output_dir + '/labels/train')
if not os.path.isdir(output_dir + '/labels/validation'):
    os.mkdir(output_dir + '/labels/validation')
if not os.path.isdir(output_dir + '/labels/test'):
    os.mkdir(output_dir + '/labels/test')

down_clothes = {9: 'skirt', 8: 'trousers', 7: 'shorts', }
up_clothes = {13: 'sling_dress', 12: 'vest_dress', 11: 'long_sleeved_dress', 10: 'short_sleeved_dress', 6: 'sling', 5: 'vest', 4: 'long_sleeved_outwear', 3: 'short_sleeved_outwear', 2: 'long_sleeved_shirt', 1: 'short_sleeved_shirt'}

def to_coco(file=1):
    if file == 1:
        input_annos_path = '/train/annos/'
        input_images_path = '/train/image/'
        output_images_path = '/images/train/'
        output_annos_path = '/labels/train/'
    elif file == 2:
        input_annos_path = '/validation/annos/'
        input_images_path = '/validation/image/'
        output_images_path = '/images/validation/'
        output_annos_path = '/labels/validation/'
    elif file == 3:
        input_annos_path = '/test/annos/'
        input_images_path = '/test/image/'
        output_images_path = '/images/test/'
        output_annos_path = '/labels/test/'
    all_images = glob(pathname=('*.*'), root_dir=standart_path + input_images_path)
    for img in tqdm(all_images):
        num = img.replace('.jpg', '')
        image_name = img
        items = []
        json_name = standart_path + input_annos_path + num +'.json'
        image_path = standart_path + input_images_path + img
        image_output_path = output_dir + output_images_path + image_name
        txt_output_path = output_dir + output_annos_path + num + '.txt'

        imag = cv2.imread(image_path)
        imag = cv2.resize(imag, (640, 640))
        cv2.imwrite(image_output_path, imag)
        with open(json_name, 'r') as f:
            temp = json.loads(f.read())
            for i in temp:
                if i == 'source' or i=='pair_id':
                    continue
                else:
                    if temp[i]['category_id'] in down_clothes:
                        cat = 0
                    else:
                        cat = 1
                    seg = temp[i]['segmentation']
                    if len(seg) == 1:
                        items = [[cat, seg]]
                    else:
                        for obj_seg in seg:
                            items.append([cat, obj_seg])
        with open(txt_output_path, "w") as f:
            for i in items:
                i[1] = list(map(str, i[1]))
                f.write(str(i[0]) + " " + " ".join(i[1]) + "\n")
to_coco()
to_coco(2)
to_coco(3)
                    