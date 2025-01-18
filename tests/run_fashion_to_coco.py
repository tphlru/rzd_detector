import deep_fashion2_to_coco
import json

to_coco = deep_fashion2_to_coco.to_coco
to_coco(r'c:/Users/Georges/Projects/datasets/DeepFashion2')
dataset = deep_fashion2_to_coco.dataset
json_name = r'c:/Users/Georges/Projects/datasets/DeepFashion2/train/train.json'
with open(json_name, 'w') as f:
    json.dump(dataset, f)

to_coco(r'c:/Users/Georges/Projects/datasets/DeepFashion2', 2)
dataset = deep_fashion2_to_coco.dataset
json_name = r'c:/Users/Georges/Projects/datasets/DeepFashion2/validation/validation.json'
with open(json_name, 'w') as f:
    json.dump(dataset, f)

to_coco(r'c:/Users/Georges/Projects/datasets/DeepFashion2', 3)
dataset = deep_fashion2_to_coco.dataset
json_name = r'c:/Users/Georges/Projects/datasets/DeepFashion2/test/test.json'
with open(json_name, 'w') as f:
    json.dump(dataset, f)
