import json
from glob import glob
from tqdm import tqdm
import os.path
import yaml
import normalized_data as nd


def create_yolo_structure(standart_dir: str):
    if not os.path.isdir(standart_dir + '/images'):
        os.mkdir(standart_dir + '/images')
    if not os.path.isdir(standart_dir + '/labels'):
        os.mkdir(standart_dir + '/labels')
    if not os.path.isdir(standart_dir + '/images/train'):
        os.mkdir(standart_dir + '/images/train')
    if not os.path.isdir(standart_dir + '/images/validation'):
        os.mkdir(standart_dir + '/images/validation')
    if not os.path.isdir(standart_dir + '/images/test'):
        os.mkdir(standart_dir + '/images/test')
    if not os.path.isdir(standart_dir + '/labels/train'):
        os.mkdir(standart_dir + '/labels/train')
    if not os.path.isdir(standart_dir + '/labels/validation'):
        os.mkdir(standart_dir + '/labels/validation')
    if not os.path.isdir(standart_dir + '/labels/test'):
        os.mkdir(standart_dir + '/labels/test')
    data = {'path': standart_dir,
        'train': standart_dir + '/images/train',
        'val': standart_dir + '/images/validation',
        'test': standart_dir + '/images/test',
        'names': {
            0: 'lower',
            1: 'higher'
        }
    }
    with open(standart_dir + "/data.yml", "w") as file:
        yaml.dump(data, file)


def get_categories_and_segmentation(json_name: str):
    down_clothes = {9: 'skirt', 8: 'trousers', 7: 'shorts', }
    #up_clothes = {13: 'sling_dress', 12: 'vest_dress', 11: 'long_sleeved_dress', 
    #10:'short_sleeved_dress', 6: 'sling', 5: 'vest', 4: 'long_sleeved_outwear', 
    #3: 'short_sleeved_outwear', 2: 'long_sleeved_shirt', 1: 'short_sleeved_shirt'} 
    #мб пригодится?
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
    return (cat, seg)


def to_coco(standart_dir, output_dir, file=1):
    if file == 1:
        input_annos_dir = '/train/annos/'
        input_images_dir = '/train/image/'
        output_images_dir = '/images/train/'
        output_annos_dir = '/labels/train/'

    elif file == 2:
        input_annos_dir = '/test/annos/'
        input_images_dir = '/test/image/'
        output_images_dir = '/images/test/'
        output_annos_dir = '/labels/test/'

    elif file == 3:
        input_annos_dir = '/validation/annos/'
        input_images_dir = '/validation/image/'
        output_images_dir = '/images/validation/'
        output_annos_dir = '/labels/validation/'

    all_images = glob(pathname=('*.*'), root_dir=standart_dir + input_images_dir)
    for img in tqdm(all_images):
        num = img.replace('.jpg', '')
        image_name = img
        items = []
        json_name = standart_dir + input_annos_dir + num +'.json'
        image_path = standart_dir + input_images_dir + img
        image_output_path = output_dir + output_images_dir + image_name
        txt_output_path = output_dir + output_annos_dir + num + '.txt'

        cat, seg = get_categories_and_segmentation(json_name=json_name)
        img_h, img_l, normalized_y = nd.cur_resize_image(image_path, image_output_path, 460)
        normalized_seg = nd.cur_resize_segmentation(h=img_h, l=img_l,normalized_x=460, normalized_y=normalized_y, seg=seg)
        print(normalized_seg)
        if len(seg) == 1:
            items = [[cat, normalized_seg]]
        else:
            for obj_seg in normalized_seg:
                items.append([cat, obj_seg])
        with open(txt_output_path, "w") as f:
            for i in items:
                i[1] = list(map(str, i[1]))
                f.write(str(i[0]) + " " + " ".join(i[1]) + "\n")


#initial directories such as standart_dir and output_dir must be WITHOUT a slash (/ or \) at the end.
deepfashion_dir = "C:/Users/Georges/Projects/datasets/DeepFashion2_standart"
yolo_dir = "C:/Users/Georges/Projects/datasets/DeepFashion2_YOLO"
create_yolo_structure(yolo_dir)
to_coco(standart_dir = deepfashion_dir, output_dir = yolo_dir)
to_coco(standart_dir = deepfashion_dir, output_dir = yolo_dir, file=2)
to_coco(standart_dir = deepfashion_dir, output_dir = yolo_dir, file=3)

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
