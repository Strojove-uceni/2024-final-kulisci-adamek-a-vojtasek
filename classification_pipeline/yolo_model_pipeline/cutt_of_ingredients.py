import os
import shutil

import yaml
from tqdm import tqdm

import project.paths as paths
import cv2
import json

# Paths
def cut_out_objects(coco_data, image_folder):
    images_folder = paths.config["images"]  # Folder containing the images
    output_folder = paths.config["cropped_objects_folder"]  # Folder to save cropped boxes

    # Clear the directory if it exists
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)  # Remove all files and subdirectories
    os.makedirs(output_folder, exist_ok=True)  # Recreate the empty directory

    for image_info in tqdm(coco_data["images"], desc="Cropping objects"):
        image_name = os.path.basename(image_info["file_name"])
        image_path = os.path.join(images_folder, image_name)
        # Check if the image exists
        if not os.path.exists(image_path):
            print(f"Image {image_path} does not exist.")
            continue

        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image {image_path}.")
            continue

        # Process each annotation for this image
        for annotation in coco_data["annotations"]:
            if annotation["image_id"] == image_info["id"]:
                x, y, w, h = map(int, annotation["bbox"])  # Bounding box (x, y, width, height)
                annotation_id = annotation["id"]

                # Crop the bounding box
                crop = image[y:y + h, x:x + w]

                # Generate output file name
                if crop.size == 0:
                    print(f"Empty crop for image {image_path}, skipping.")
                    continue
                crop_filename = f"{os.path.splitext(image_name)[0]}_ann_{annotation_id}.jpg"
                crop_path = os.path.join(output_folder, crop_filename)

                # Save the cropped image
                cv2.imwrite(crop_path, crop)

    # print(f"Cropping completed. Cropped images saved to {output_folder}.")

# with open(paths.config["yolo_results"], "r") as f:
#     coco_data = yaml.safe_load(f)
# cut_out_objects(coco_data)