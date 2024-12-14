import json
import os
import re

import yaml
from tqdm import tqdm

import project.paths as paths
from project.recipe_dataset.ingredients_functions import load_ingredients
from clip_model import ClipModel
from predict_labels import predict

composite_ingredients, single_ingredients = load_ingredients(paths.config["ingredients_dict"])

ingredients = composite_ingredients + single_ingredients
clip_model = ClipModel()

# clip_model.load_label_embeddings("./embedded_labels")
clip_model.embed_labels(ingredients)
clip_labels = predict(clip_model)

# Assuming you have YOLO results saved as COCO-like JSON

with open(paths.config["yolo_results"], "r") as f:
    coco_data = json.load(f)

# Add new categories for CLIP predictions
label_list = list(clip_model._label_embeddings.keys())
for label in tqdm(label_list):
    # Add a new category for each unique CLIP label that is not already in YOLO's categories
    coco_data["categories"].append({
        "id": label_list.index(label),
        "name": label,
    })

# Merge CLIP predictions into COCO annotations
annotation_id = 0

reverse_dictionary_path = paths.config["reversed_ingredients_dict"]
with open(reverse_dictionary_path, "r") as f:
    reverse_dictionary = yaml.safe_load(f)

for image_path, label in clip_labels.items():
    # Extract image file name from the path
    file_name = os.path.basename(image_path)
    # Get the corresponding image ID from the YOLO JSON
    object_id = int(re.search(r'ann_(\d+)', file_name)[1])
    # Add a new annotation for the classification result from CLIP
    coco_data["annotations"][object_id]["category_id"] = label_list.index(label)


# Save the updated COCO-like JSON with both YOLO and CLIP results
output_file = paths.config["clip_results"]
with open(output_file, "w") as f:
    json.dump(coco_data, f, indent=4)

print(f"Combined YOLO and CLIP COCO-like JSON saved to {output_file}")
