import os
import shutil

import cv2
import json

# Paths
coco_json_path = "../results/yolo_results.json"  # Path to the COCO annotations JSON
images_folder = "../images/"  # Folder containing the image
output_folder = "../results/yolo_objects_cropped"  # Folder to save cropped boxes

# Clear the directory if it exists
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)  # Remove all files and subdirectories
os.makedirs(output_folder, exist_ok=True)  # Recreate the empty directory

# Load the COCO JSON
with open(coco_json_path, "r") as f:
    coco_data = json.load(f)

# Extract the image details
image_info = coco_data["images"][0]  # Only one image
image_filename = image_info["file_name"]
image_path = os.path.join(images_folder, image_filename)

# Check if the image exists
if not os.path.exists(image_path):
    print(f"Image {image_path} does not exist.")
    exit()

# Load the image
image = cv2.imread(image_path)
if image is None:
    print(f"Failed to load image {image_path}.")
    exit()

# Process each annotation
for annotation in coco_data["annotations"]:
    x, y, w, h = map(int, annotation["bbox"])  # Bounding box (x, y, width, height)
    category_id = annotation["category_id"]
    annotation_id = annotation["id"]

    # Crop the bounding box
    crop = image[y:y + h, x:x + w]

    # Generate output file name
    crop_filename = f"{os.path.splitext(image_filename)[0]}_ann_{annotation_id}_cat_{category_id}.jpg"
    crop_path = os.path.join(output_folder, crop_filename)

    # Save the cropped image
    cv2.imwrite(crop_path, crop)

print(f"Cropping completed. Cropped images saved to {output_folder}.")