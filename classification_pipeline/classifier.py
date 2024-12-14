import json
import os
import re
from typing import Optional

import cv2
import yaml
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

import project.paths as paths
from project.classification_pipeline.clip_model_pipeline.clip_model import ClipModel
from project.classification_pipeline.yolo_model_pipeline.cutt_of_ingredients import cut_out_objects
from project.classification_pipeline.yolo_model_pipeline.models.YOLO_model import YoloModel


class IngredientClassifier():
    def __init__(self):
        self.yolo_model = YoloModel()
        self.clip_model = ClipModel()

    def inference(self, image_folder, iou_threshold=0.8, visualize=False) -> (dict, list):
        """
        Run inference on images in a folder.

        Args:
            image_folder (str): Path to the folder containing images to process.
            iou_threshold (float): Intersection over Union (IoU) threshold for filtering YOLO predictions.
            visualize (bool): If True, return images with bounding boxes and annotations drawn on them.

        Returns:
            Tuple[dict, list]:
                - A dictionary where the keys are image paths and the values are PIL images with annotations drawn.
                - A list of lists of detected ingredients, one list per image.
        """
        output_file = paths.config["yolo_results"]

        # Load the unified labels
        with open(paths.config["reversed_ingredients_dict"]) as f:
            unified_labels = yaml.safe_load(f)

        unified_labels_list = list(set(unified_labels.values()))
        print(f"Unified Labels: {unified_labels_list}")

        # YOLO inference
        coco_data = self.yolo_model.detect(image_folder, output_file, iou_threshold=iou_threshold, save=True)

        # Cut out objects from images (for CLIP classification)
        cut_out_objects(coco_data, image_folder)

        # Load CLIP embeddings
        self.clip_model.load_label_embeddings(paths.config["embedded_labels"])

        # Add category labels for the unified labels
        for label in unified_labels_list:
            coco_data["categories"].append({
                "id": unified_labels_list.index(label),
                "name": label,
            })

        cropped_obj = paths.config["cropped_objects_folder"]

        # Classify each cropped image using the CLIP model
        for file_name in tqdm(os.listdir(cropped_obj), desc="Classifying ingredients"):
            if file_name.endswith((".jpg", ".png", ".jpeg")):  # Only process image files
                object_id = int(re.search(r'ann_(\d+)', file_name)[1])  # Extract object ID from file name
                image_path = os.path.join(cropped_obj, file_name)
                label = self.clip_model.label_image(image_path)  # Predict ingredient label using CLIP
                coco_data["annotations"][object_id]["category_id"] = unified_labels_list.index(unified_labels[label])

        # Save the updated COCO annotations
        with open(paths.config["clip_results"], "w") as f:
            json.dump(coco_data, f, indent=4)

        # If visualization is enabled, draw bounding boxes and return the images
        if visualize:
            images_with_annotations = self.add_bboxes_and_annotation(coco_data)

            # Extract the list of detected ingredients for each image
            detected_ingredients = []
            for image_path, image in images_with_annotations.items():
                image_ingredients = []
                for annotation in coco_data['annotations']:
                    if annotation['image_id'] == self.get_image_id_from_path(image_path, coco_data['images']):
                        category_id = annotation.get('category_id', None)
                        if category_id is not None:
                            label = self.get_label_from_category_id(category_id, coco_data['categories'])
                            image_ingredients.append(label)
                detected_ingredients.append(image_ingredients)

            return images_with_annotations, detected_ingredients
        else:
            detected_ingredients = []
            for image_dict in coco_data['images']:
                image_id = image_dict['id']
                image_ingredients = []
                for annotation in coco_data['annotations']:
                    if annotation['image_id'] == image_id:
                        category_id = annotation.get('category_id', None)
                        if category_id is not None:
                            label = self.get_label_from_category_id(category_id, coco_data['categories'])
                            image_ingredients.append(label)
                detected_ingredients.append(image_ingredients)

            return {}, detected_ingredients

    def get_image_id_from_path(self, image_path: str, images: list) -> Optional[int]:
        """
        Get the image ID for a given image path from the COCO images list.

        Args:
            image_path (str): Path to the image.
            images (list): List of image dictionaries from the COCO JSON.

        Returns:
            int: The image ID if found, otherwise None.
        """
        for image in images:
            if os.path.basename(image['file_name']) == os.path.basename(image_path):
                return image['id']
        return None

    def get_label_from_category_id(self, category_id: int, categories: list) -> Optional[str]:
        """
        Get the label (ingredient name) corresponding to a category_id.

        Args:
            category_id (int): The ID of the category.
            categories (list): List of category dictionaries from the COCO JSON.

        Returns:
            str: The name of the category if found, otherwise None.
        """
        for category in categories:
            if category['id'] == category_id:
                return category['name']
        return None
    def add_bboxes_and_annotation(self, coco_data) -> Image:

        # Get image details
        category_dict = {category['id']: category['name'] for category in coco_data['categories']}
        images = {}
        for image_dict in coco_data["images"]:
            image_path = image_dict['file_name']
            image_id = image_dict['id']
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



