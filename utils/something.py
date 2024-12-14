import json
import os
import shutil

# Configuration
coco_json_path = '../coco_dataset/annotations/instances_.json'  # Path to your COCO JSON file
image_directory = './coco_dataset/'         # Path to the folder containing images
split_index = 900                                # Number of images in the first split
split_1_output_path = '../coco_dataset/annotations/instances_split_1.json'  # Path to save split 1 JSON
split_2_output_path = '../coco_dataset/annotations/instances_split_2.json'  # Path to save split 2 JSON
split_1_image_dir = '../coco_dataset/split_1_images'  # Directory for images in split 1
split_2_image_dir = '../coco_dataset/split_2_images'  # Directory for images in split 2

# Create directories for images
os.makedirs(split_1_image_dir, exist_ok=True)
os.makedirs(split_2_image_dir, exist_ok=True)

# Load the COCO JSON file
with open(coco_json_path, 'r') as file:
    data = json.load(file)

# Sort images by their ID to ensure consistent splitting
data['images'].sort(key=lambda x: x['id'])

# Split images into two groups
images_split_1 = data['images'][:split_index]
images_split_2 = data['images'][split_index:]

# Extract image IDs for split 1 and split 2
image_ids_split_1 = {img['id'] for img in images_split_1}
image_ids_split_2 = {img['id'] for img in images_split_2}

# Split annotations into two groups based on image_id
annotations_split_1 = [ann for ann in data['annotations'] if ann['image_id'] in image_ids_split_1]
annotations_split_2 = [ann for ann in data['annotations'] if ann['image_id'] in image_ids_split_2]

# Copy categories and info (they are usually shared across both datasets)
categories = data['categories']
info = data.get('info', {})

# Create two new COCO datasets
split_1 = {
    'info': info,
    'images': images_split_1,
    'annotations': annotations_split_1,
    'categories': categories
}

split_2 = {
    'info': info,
    'images': images_split_2,
    'annotations': annotations_split_2,
    'categories': categories
}

# Save the two new COCO JSON files
with open(split_1_output_path, 'w') as file:
    json.dump(split_1, file, indent=4)

with open(split_2_output_path, 'w') as file:
    json.dump(split_2, file, indent=4)

print(f"✅ Dataset split saved as: \n 1️⃣ {split_1_output_path} \n 2️⃣ {split_2_output_path}")

# Move images into separate folders
for image in images_split_1:
    source_path = os.path.join(image_directory, image['file_name'])
    destination_path = os.path.join(split_1_image_dir, image['file_name'])
    if os.path.exists(source_path):
        shutil.copy(source_path, destination_path)
    else:
        print(f"⚠️ Image not found: {source_path}")

for image in images_split_2:
    source_path = os.path.join(image_directory, image['file_name'])
    destination_path = os.path.join(split_2_image_dir, image['file_name'])
    if os.path.exists(source_path):
        shutil.copy(source_path, destination_path)
    else:
        print(f"⚠️ Image not found: {source_path}")

print(f"✅ Images successfully moved to: \n 📁 {split_1_image_dir} \n 📁 {split_2_image_dir}")
