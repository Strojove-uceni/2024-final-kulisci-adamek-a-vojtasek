import os
import cv2
import yaml
import project.paths as paths
from project.classification_pipeline.clip_model_pipeline.clip_model import ClipModel
def predict(clip_model: ClipModel) -> dict:
    input_folder = paths.config["cropped_objects_folder"]
    # Iterate over all files in the folder
    labels = {}
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".jpg"):  # Process only .jpg files
            image_path = os.path.join(input_folder, file_name)

            label = clip_model.label_image(image_path)
            labels[image_path] = label

    return labels