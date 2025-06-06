import json
import cv2
from glob import glob
from tqdm import tqdm
import os.path

dataset = {
    "info": {
        'description': 'LABORAD\'s modified for trainning segmetation Deepfashion2',
        'version': 1.0,
        'year': 2025,
        'contribytor': 'LABORAD',
        'date_created': "2025/01/18"
    },
    "licenses": [],
    "images": [],
    "annotations": [],
    "categories": []
}

'''
----Data structure----
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
        
'''

down_clothes = {9: 'skirt', 8: 'trousers', 7: 'shorts', }
up_clothes = {13: 'sling_dress', 12: 'vest_dress', 11: 'long_sleeved_dress', 10: 'short_sleeved_dress', 6: 'sling', 5: 'vest', 4: 'long_sleeved_outwear', 3: 'short_sleeved_outwear', 2: 'long_sleeved_shirt', 1: 'short_sleeved_shirt'}

dataset['categories'].append({
    'id': 1,
    'name': "higher",
    'supercategory': "clothes"
})

dataset['categories'].append({
    'id': 2,
    'name': "lower",
    'supercategory': "clothes"
})


def to_coco(standart_path, file=1):
    sub_index = 0 # the index of ground truth instance
    if file == 1:
        annos_path = '/train/annos/'
        images_path = '/train/image/'
    elif file == 2:
        annos_path = '/validation/annos/'
        images_path = '/validation/image/'
    elif file == 3:
        annos_path = '/test/annos/'
        images_path = '/test/image/'
    num_images = len(glob(pathname=('*.*'), root_dir=standart_path + images_path))
    for num in tqdm(range(1, num_images+1)):
        json_name = standart_path + annos_path + str(num).zfill(6)+'.json'
        image_name = standart_path + images_path + str(num).zfill(6)+'.jpg'

        if (num>=0 and os.path.isfile(image_name)):
            imag = cv2.imread(image_name)
            imag = cv2.resize(imag, (640, 640))
            cv2.imwrite(image_name, imag)
            width = 640
            height = 640
            with open(json_name, 'r') as f:
                temp = json.loads(f.read())
                dataset['images'].append({
                    'coco_url': '',
                    'date_captured': '',
                    'file_name': str(num).zfill(6) + '.jpg',
                    'flickr_url': '',
                    'id': num,
                    'license': 0,
                    'width': width,
                    'height': height
                })
                for i in temp:
                    if i == 'source' or i=='pair_id':
                        continue
                    else:
                        sub_index = sub_index + 1
                        if temp[i]['category_id'] in down_clothes:
                            cat = 1
                        else:
                            cat = 2
                        seg = temp[i]['segmentation']

                        dataset['annotations'].append({
                            'area': width*height,
                            'category_id': cat,
                            'id': sub_index,
                            'image_id': num,
                            'iscrowd': 0,
                            'segmentation': seg,
                        })


