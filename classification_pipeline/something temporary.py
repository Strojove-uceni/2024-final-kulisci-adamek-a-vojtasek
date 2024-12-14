import json
import os

from project.recipe_dataset.ingredients_functions import load_ingredients
import clip_model_pipeline.clip_model as clip
from clip_model_pipeline.predict_labels import predict



composite_ingredients, single_ingredients = load_ingredients(
    "../ingredients_configs/ingredients_config.yaml")

ingredients = composite_ingredients + single_ingredients
clip_model = clip.ClipModel()

clip_model.load_label_embeddings("./clip_model_pipeline/embedded_labels")
clip_labels = predict(clip_model)

# Assuming you have YOLO results saved as COCO-like JSON
yolo_results_path = "results/yolo_results.json"

# Load YOLO results JSON
with open(yolo_results_path, "r") as f:
    coco_data = json.load(f)

# Extract existing category mapping from YOLO JSON
category_mapping = {cat["name"]: cat["id"] for cat in coco_data["categories"]}
category_id = max(category_mapping.values()) + 1  # Start after the last existing category ID

# Add new categories for CLIP predictions
for label in set(clip_labels.values()):
    if label not in category_mapping:
        # Add a new category for each unique CLIP label that is not already in YOLO's categories
        coco_data["categories"].append({
            "id": category_id,
            "name": label,
            "supercategory": "ingredient"
        })
        category_mapping[label] = category_id
        category_id += 1

# Merge CLIP predictions into COCO annotations
annotation_id = len(coco_data["annotations"])  # Start from the last annotation ID
image_mapping = {image["file_name"]: image["id"] for image in coco_data["images"]}  # Mapping filenames to image IDs

for image_path, label in clip_labels.items():
    # Extract image file name from the path
    file_name = os.path.basename(image_path)

    # Get the corresponding image ID from the YOLO JSON
    if file_name in image_mapping:
        image_id = image_mapping[file_name]

        # Add a new annotation for the classification result from CLIP
        coco_data["annotations"].append({
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_mapping[label],  # Use the category ID from the mapping
            "iscrowd": 0,
            "score": 1.0  # Optional, set a default confidence score for classification
        })
        annotation_id += 1
    else:
        print(f"Warning: Image {file_name} not found in YOLO results. Skipping...")

# Save the updated COCO-like JSON with both YOLO and CLIP results
output_file = "../results/annotations/clip_results.json"
with open(output_file, "w") as f:
    json.dump(coco_data, f, indent=4)

print(f"Combined YOLO and CLIP COCO-like JSON saved to {output_file}")