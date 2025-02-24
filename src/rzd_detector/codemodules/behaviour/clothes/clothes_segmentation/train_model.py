from ultralytics import YOLO

# Load a model
model = YOLO("yolo11n.pt")  # load a pretrained model (recommended for training)

# Train the model
results = model.train(data=r"C:\Users\Georges\Projects\datasets\DeepFashion2_YOLO\data.yml", epochs=100, imgsz=640, save=True)
