import json
import os
import re
from collections import defaultdict

import cv2
import yaml
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

import project.paths as paths
from project.classification_pipeline.clip_model_pipeline.clip_model import ClipModel
from project.classification_pipeline.yolo_model_pipeline.cutt_of_ingredients import cut_out_objects
from project.classification_pipeline.yolo_model_pipeline.YOLO_model import YoloModel


class IngredientClassifier():
    def __init__(self):
        self.yolo_model = YoloModel()
        self.clip_model = ClipModel()

    def inference(self, image_folder, iou_threshold=0.7) -> Image:
        output_file = paths.config["yolo_results"]
        with open(paths.config["reversed_ingredients_dict"]) as f:
            unified_labels = yaml.safe_load(f)
        coco_data = self.yolo_model.detect(image_folder, output_file, iou_threshold=iou_threshold, save=True)
        cut_out_objects(coco_data, image_folder)

        self.clip_model.load_label_embeddings(paths.config["embedded_labels"])
        # clip_labels = predict(self.clip_model)
        cropped_obj = paths.config["cropped_objects_folder"]
        unified_labels_list = list(set(unified_labels.values()))
        for label in unified_labels_list:
            coco_data["categories"].append({
                "id": unified_labels_list.index(label),
                "name": label,
            })

        # for image_path, label in clip_labels.items():

        for file_name in tqdm(os.listdir(cropped_obj), desc="Classifying ingredients"):
            if file_name.endswith(".jpg") or file_name.endswith(".png") or file_name.endswith(".jpeg"):  # Process only .jpg files
                # Extract image file name from the path
                # Get the corresponding image ID from the YOLO JSON
                object_id = int(re.search(r'ann_(\d+)', file_name)[1])
                # Add a new annotation for the classification result from CLIP
                image_path = os.path.join(cropped_obj, file_name)
                label = self.clip_model.label_image(image_path)
                coco_data["annotations"][object_id]["category_id"] = unified_labels_list.index(unified_labels[label])
        with open(paths.config["clip_results"], "w") as f:
            json.dump(coco_data, f, indent=4)
        ingreds = extract_ingredients_from_coco(coco_data)
        return self.add_bboxes_and_annotation(coco_data), ingreds
        # return coco_data



    def add_bboxes_and_annotation(self, coco_data) -> Image:

        # Get image details
        category_dict = {category['id']: category['name'] for category in coco_data['categories']}
        images = {}
        for image_dict in coco_data["images"]:
            image_path = image_dict['file_name']
            image_id = image_dict['id']
            image_path = os.path.join(paths.config["images"], os.path.basename(image_path))
            # Check if the image exists
            if not os.path.exists(image_path):
                print(f"Image {image_path} does not exist.")
                return

            # Load the image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                print(f"Failed to load image {image_path}.")
                return

            # Convert the OpenCV image (BGR) to RGB format and then to PIL Image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image)
            # Draw all annotations related to this image
            draw = ImageDraw.Draw(pil_image)
            for annotation in coco_data['annotations']:
                # Extract bounding box information (if available)
                id = annotation['image_id']
                if id == image_id:
                    bbox = annotation.get('bbox', None)
                    category_id = annotation['category_id']
                    label = category_dict[category_id]

                    # Draw the bounding box if available
                    if bbox:
                        x_min, y_min, width, height = bbox
                        x_max, y_max = x_min + width, y_min + height

                        # Draw rectangle for bounding box
                        color_rec = (0, 255, 0)  # Green
                        draw.rectangle([x_min, y_min, x_max, y_max], outline=color_rec, width=2)

                        # Draw label above the bounding box
                        font = ImageFont.load_default(40)
                        text_position = (x_min, y_min - 10 if y_min - 10 > 10 else y_min + 10)
                        color_text = (0, 255, 0)
                        draw.text(text_position, label, fill=color_text, font=font)
                images[image_path] = pil_image
        return images



def extract_ingredients_from_coco(coco_data) -> dict:
    """
    Extracts a dictionary where each image ID is mapped to a list of ingredients present in that image.

    Args:
        coco_json_path (str): Path to the COCO-like JSON file.

    Returns:
        dict: A dictionary where the keys are image file names and the values are lists of ingredients.
    """

    # Create a lookup dictionary for category_id -> ingredient name
    category_id_to_name = {category['id']: category['name'] for category in coco_data['categories']}

    # Create a dictionary to store ingredients for each image
    image_ingredients = defaultdict(list)

    # Iterate over the annotations and collect ingredients for each image
    for annotation in coco_data['annotations']:
        image_id = annotation['image_id']
        category_id = annotation.get('category_id', None)

        # Get the file name for the corresponding image_id
        image_filename = None
        for image in coco_data['images']:
            if image['id'] == image_id:
                image_filename = f"{paths.config["annotated_images"]}/{os.path.basename(image['file_name'])}"
                break

        # Skip if the image file name is not found or the category_id is missing
        if image_filename is None or category_id is None:
            continue

        # Get the ingredient name corresponding to the category_id
        ingredient_name = category_id_to_name.get(category_id, None)

        # Add the ingredient name to the image's list of ingredients
        if ingredient_name is not None and ingredient_name not in image_ingredients[image_filename]:
            image_ingredients[image_filename].append(ingredient_name)

    return dict(image_ingredients)



