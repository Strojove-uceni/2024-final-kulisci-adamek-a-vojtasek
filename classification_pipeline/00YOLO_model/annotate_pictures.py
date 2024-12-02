import json
from ultralytics import YOLO

# Load the YOLO models
model1 = YOLO("models/for_vegetables.pt")  # First model
model2 = YOLO("models/for_packed.pt")  # Second model

# Run inference on the same image with both models
image_name = "sarah.jpg"
image_path = "/home/petr/Documents/SU2_project/project/classification_pipeline/images/"+ image_name
results1 = model1([image_path], conf=0.1)
results2 = model2([image_path], conf=0.1)

# Initialize COCO-like structure
coco_data = {
    "info": {
        "description": "Model Inference Results",
        "version": "1.0",
        "year": 2024,
        "contributor": "Your Name",
        "date_created": "2024-11-30"
    },
    "images": [],
    "annotations": [],
    "categories": [
        {"id": 1, "name": "object_model1", "supercategory": "none"},
        {"id": 2, "name": "object_model2", "supercategory": "none"}  # Separate category for second model
    ]
}

annotation_id = 0
image_id = 0

# Add image information (common for both models)
coco_data["images"].append({
    "id": image_id,
    "file_name": image_name,
    "width": results1[0].orig_shape[1],
    "height": results1[0].orig_shape[0]
})

# Process results from the first model
for result in results1:
    boxes = result.boxes
    if boxes is not None:
        for i, box in enumerate(boxes.xyxy):
            x_min, y_min, x_max, y_max = map(float, box)  # Bounding box in [x_min, y_min, x_max, y_max]
            width = x_max - x_min
            height = y_max - y_min
            score = float(boxes.conf[i])  # Confidence score
            category_id = 1  # Category ID for model1

            # Add annotation
            coco_data["annotations"].append({
                "id": annotation_id,
                "image_id": image_id,
                "category_id": category_id,
                "bbox": [x_min, y_min, width, height],
                "area": width * height,
                "iscrowd": 0,
                "score": score
            })
            annotation_id += 1

# Process results from the second model
for result in results2:
    boxes = result.boxes
    if boxes is not None:
        for i, box in enumerate(boxes.xyxy):
            x_min, y_min, x_max, y_max = map(float, box)  # Bounding box in [x_min, y_min, x_max, y_max]
            width = x_max - x_min
            height = y_max - y_min
            score = float(boxes.conf[i])  # Confidence score
            category_id = 2  # Category ID for model2

            # Add annotation
            coco_data["annotations"].append({
                "id": annotation_id,
                "image_id": image_id,
                "category_id": category_id,
                "bbox": [x_min, y_min, width, height],
                "area": width * height,
                "iscrowd": 0,
                "score": score
            })
            annotation_id += 1

# Save results to a COCO-like JSON file
output_file = "../results/yolo_results.json"
with open(output_file, "w") as f:
    json.dump(coco_data, f, indent=4)

print(f"Combined COCO-like JSON saved to {output_file}")
