import abc
import json
import os

from tqdm import tqdm

import project.paths as paths
from charset_normalizer import detect
from ultralytics import YOLO


class YoloModel(abc.ABC):
    def __init__(self, path_to_model:str = None):
        if not path_to_model:
            self.model1 = YOLO(paths.config["yolo_model_1"])
            self.model2 = YOLO(paths.config["yolo_model_2"])

    def detect(self, folder_path, output_file, iou_threshold=0.7, save: bool = False):

        # List all images in the folder
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # Initialize COCO format data
        coco_data = {
            "info": {
                "description": "Model Inference Results with NMS",
                "version": "2.0",
                "year": 2024,
                "contributor": "Petr and Filip",
            },
            "images": [],
            "annotations": [],
            "categories": []
        }

        image_id = 0  # To keep track of image ids
        annotation_id = 0  # To keep track of annotation ids

        for image_name in tqdm(image_files, desc="Object detection"):
            image_path = os.path.join(folder_path, image_name)

            results1 = self.model1([image_path], conf=0.1, verbose=False)
            results2 = self.model2([image_path], conf=0.05, verbose=False)

            image_info = {
                "id": image_id,
                "file_name": "images/" + image_name,
                "width": results1[0].orig_shape[1],
                "height": results1[0].orig_shape[0],
            }

            coco_data["images"].append(image_info)

            all_detections = []

            # Extract detections from model1
            for result in results1:
                boxes = result.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes.xyxy):
                        x_min, y_min, x_max, y_max = map(float, box)
                        width = x_max - x_min
                        height = y_max - y_min
                        score = float(boxes.conf[i])
                        model_id = 1  # Category ID for model1
                        all_detections.append({
                            "bbox": [x_min, y_min, width, height],
                            "confidence": score,
                            "model": model_id,
                        })

            # Extract detections from model2
            for result in results2:
                boxes = result.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes.xyxy):
                        x_min, y_min, x_max, y_max = map(float, box)
                        width = x_max - x_min
                        height = y_max - y_min
                        score = float(boxes.conf[i])
                        model_id = 2  # Category ID for model2
                        all_detections.append({
                            "bbox": [x_min, y_min, width, height],
                            "confidence": score,
                            "model": model_id
                        })

            # Perform Non-Maximum Suppression (NMS)
            nms_detections = self.non_max_suppression(all_detections, iou_threshold=iou_threshold)

            # Add annotations from NMS filtered detections
            for detection in nms_detections:
                x_min, y_min, width, height = detection["bbox"]
                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "bbox": [int(x_min), int(y_min), int(width), int(height)],
                    "area": int(width * height),
                    "iscrowd": 0,
                    "segmentation": [],
                    "category_id": 0,
                })
                annotation_id += 1

            image_id += 1  # Increment image id for each new image

        if save:
            with open(output_file, "w") as f:
                json.dump(coco_data, f, indent=4)

        return coco_data

    def non_max_suppression(self, detections, iou_threshold=0.8):
        """Apply Non-Maximum Suppression to a list of detections."""
        detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        nms_detections = []

        while detections:
            best_detection = detections.pop(0)
            nms_detections.append(best_detection)

            # Remove detections that overlap too much with the best detection
            detections = [
                det for det in detections
                if self.calculate_iou(best_detection['bbox'], det['bbox']) < iou_threshold
            ]

        return nms_detections

    def calculate_iou(self, box1, box2):
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        x1_min, y1_min, x1_max, y1_max = box1[0], box1[1], box1[0] + box1[2], box1[1] + box1[3]
        x2_min, y2_min, x2_max, y2_max = box2[0], box2[1], box2[0] + box2[2], box2[1] + box2[3]

        # Calculate intersection
        xi1 = max(x1_min, x2_min)
        yi1 = max(y1_min, y2_min)
        xi2 = min(x1_max, x2_max)
        yi2 = min(y1_max, y2_max)
        intersection_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

        # Calculate areas of each box
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)

        # Calculate union
        union_area = box1_area + box2_area - intersection_area

        # IoU
        if union_area == 0:
            return 0
        return intersection_area / union_area