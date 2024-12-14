from ultralytics import YOLO

model = YOLO("yolov8m.pt")  # load a pretrained model (recommended for training)

# Train the model
results = model.train(
    data="/mnt/home2/SU2/ingredients_photo_dataset/final_dataset/dataset.yaml",
    epochs=400,
    imgsz=640,
    device=0,  # Specify GPU device
    batch=8,  # Reduce if you face memory issues
    save_period=10,  # Save weights after each epoch (useful for debugging)
    name="yolo11n-experiment",
)