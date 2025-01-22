import deep_fashion2_to_coco as deep_fashion2_to_coco
import json

standart_path = r"C:\Users\Georges\Projects\datasets\DeepFashion2_standart"

to_coco = deep_fashion2_to_coco.to_coco
to_coco(standart_path)
dataset = deep_fashion2_to_coco.dataset
json_name = r'C:\Users\Georges\Projects\datasets\DeepFashion2_Coco\annotations\train.json'
with open(json_name, 'w') as f:
    json.dump(dataset, f)

to_coco(standart_path, 2)
dataset = deep_fashion2_to_coco.dataset
json_name = r'C:\Users\Georges\Projects\datasets\DeepFashion2_Coco\annotations\validation.json'
with open(json_name, 'w') as f:
    json.dump(dataset, f)

to_coco(standart_path, 3)
dataset = deep_fashion2_to_coco.dataset
json_name = r'C:\Users\Georges\Projects\datasets\DeepFashion2_Coco\annotations\test.json'
with open(json_name, 'w') as f:
    json.dump(dataset, f)
