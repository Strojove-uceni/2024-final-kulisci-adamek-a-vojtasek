import os
import glob
import numpy as np

def is_correct_format(bbox):
    """
    Check if the bounding box format is correct (xywh format).
    A correct format should contain 4 numbers.
    """
    return len(bbox) == 4

def convert_polygon_to_xywh(bbox):
    """
    Convert bounding box from polygon to (x_center, y_center, width, height).
    If the polygon has 10 points (repeated first point to close the polygon), it removes the redundant point.
    """
    if len(bbox) == 10 and bbox[:2] == bbox[-2:]:
        bbox = bbox[:-2]  # Remove the redundant last point

    x_coords = bbox[0::2]
    y_coords = bbox[1::2]
    x_min = min(x_coords)
    y_min = min(y_coords)
    x_max = max(x_coords)
    y_max = max(y_coords)

    x_center = (x_min + x_max) / 2.0
    y_center = (y_min + y_max) / 2.0
    width = x_max - x_min
    height = y_max - y_min

    return [x_center, y_center, width, height]

def process_label_file(label_file_path):
    """
    Process a single label file to convert bounding boxes only if they are not in the correct format.
    """
    with open(label_file_path, 'r') as file:
        lines = file.readlines()

    converted_lines = []
    for line in lines:
        elements = line.strip().split()
        class_id = elements[0]
        bbox = list(map(float, elements[1:]))

        if not is_correct_format(bbox):
            # Convert if the format is incorrect
            bbox_xywh = convert_polygon_to_xywh(bbox)
            if bbox_xywh:
                bbox = bbox_xywh
            print(f"Checked and converted: {label_file_path}")

        bbox = [f"{coord:.6f}" for coord in bbox]
        converted_line = f"{class_id} " + " ".join(bbox) + "\n"
        converted_lines.append(converted_line)

    with open(label_file_path, 'w') as file:
        file.writelines(converted_lines)

def convert_labels_in_folder(folder_path):
    """
    Iterate through all label files in the given folder and convert them if necessary.
    """
    label_files = glob.glob(os.path.join(folder_path, '*.txt'))
    for label_file in label_files:
        process_label_file(label_file)


def main():
    base_path = "/mnt/home2/ingredients_photo_dataset/Fridgify_Dataset/"  # Base folder containing train, val, test subfolders
    subsets = ["train/labels", "valid/labels", "test/labels"]

    for subset in subsets:
        folder_path = os.path.join(base_path, subset)
        print(folder_path)
        if os.path.exists(folder_path):
            convert_labels_in_folder(folder_path)
        else:
            print(f"Warning: Folder {folder_path} does not exist.")

if __name__ == "__main__":
    main()
