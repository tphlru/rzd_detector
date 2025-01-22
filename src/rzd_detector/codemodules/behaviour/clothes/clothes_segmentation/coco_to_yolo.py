from ultralytics.data.converter import convert_coco

convert_coco(labels_dir=r"C:\Users\Georges\Projects\datasets\DeepFashion2_Coco\annotations", save_dir=r"C:\Users\Georges\Projects\datasets\DeepFashion2_YOLO", use_segments=True)