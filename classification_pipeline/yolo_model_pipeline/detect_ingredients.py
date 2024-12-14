import json
import os
from ultralytics import YOLO
import numpy as np
import project.paths as paths

from project.classification_pipeline.yolo_model_pipeline.models.YOLO_model import YoloModel







def main():
    # Load the YOLO models
    # Run inference on the same image with both models
    image_name = "cerne.jpg"
    # output_file = "/home/petr/Documents/SU2_project/project/classification_pipeline/results/yolo_results.json"
    output_file = paths.config["yolo_results"]
    yolo = YoloModel()
    yolo.detect(image_name, output_file, save=True)
    print(f"COCO-like JSON saved with combined YOLO and NMS results to {output_file}")

if __name__ == "__main__":
    main()
