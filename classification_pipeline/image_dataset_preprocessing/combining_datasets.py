import os
import glob
import shutil

def rewrite_label_to_binary(label_file_path, output_label_file_path, new_label):
    """
    Rewrite all labels in a given label file to the specified new label.
    """
    with open(label_file_path, 'r') as file:
        lines = file.readlines()

    rewritten_lines = []
    for line in lines:
        elements = line.strip().split()
        # Replace the class_id with the new label (either 0 or 1)
        bbox = elements[1:]
        new_line = f"{new_label} " + " ".join(bbox) + "\n"
        rewritten_lines.append(new_line)

    # Write the new label lines to the output label file
    with open(output_label_file_path, 'w') as file:
        file.writelines(rewritten_lines)

def combine_datasets(base_paths, output_base_path, new_label):
    """
    Combine datasets from multiple base paths into a new dataset and rewrite labels to a single new label.
    Also, copy the corresponding images to the new dataset.
    """
    subsets = ["train", "valid", "test"]
    for subset in subsets:
        # Create output folders for the combined dataset (images and labels)
        output_label_folder = os.path.join(output_base_path, subset, 'labels')
        output_image_folder = os.path.join(output_base_path, subset, 'images')
        os.makedirs(output_label_folder, exist_ok=True)
        os.makedirs(output_image_folder, exist_ok=True)

        for base_path in base_paths:
            input_label_folder = os.path.join(base_path, subset, 'labels')
            input_image_folder = os.path.join(base_path, subset, 'images')

            if os.path.exists(input_label_folder):
                label_files = glob.glob(os.path.join(input_label_folder, '*.txt'))
                for label_file in label_files:
                    output_label_file_path = os.path.join(output_label_folder, os.path.basename(label_file))
                    if not os.path.exists(output_label_file_path):
                        rewrite_label_to_binary(label_file, output_label_file_path, new_label)
                        print(f"Rewritten label for: {label_file} to {output_label_file_path}")
                    else:
                        print(f"Skipped existing label file: {output_label_file_path}")

            if os.path.exists(input_image_folder):
                image_files = glob.glob(os.path.join(input_image_folder, '*.jpg'))
                for image_file in image_files:
                    output_image_file_path = os.path.join(output_image_folder, os.path.basename(image_file))
                    if not os.path.exists(output_image_file_path):
                        shutil.copy(image_file, output_image_file_path)
                        print(f"Copied image: {image_file} to {output_image_file_path}")
                    else:
                        print(f"Skipped existing image file: {output_image_file_path}")

def create_yaml_file(output_base_path):
    """
    Create a dataset YAML file for the combined dataset.
    """
    yaml_content = f"""
    train: {output_base_path}/train/images
    val: {output_base_path}/valid/images
    test: {output_base_path}/test/images

    nc: 1  # Number of classes (since all labels are either 0 or 1)
    names: ['combined_label']  # Name of the single class
    """

    yaml_file_path = os.path.join(output_base_path, "dataset.yaml")
    with open(yaml_file_path, 'w') as file:
        file.write(yaml_content)
    print(f"YAML file created at: {yaml_file_path}")

if __name__ == "__main__":
    # List of dataset base paths to combine
    base_paths = [
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/Dataset for YOLOv5.v2i.yolov11",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/EzyCart",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/food_ingredients_dataset",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/food_ingreds_num44",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/Fridgify_Dataset",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/Fruits_and_vegetables",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/grocery_items",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/Ingredients_YOLO.v3:ingredients-dataset:3.0.yolov11",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/Maydanoz.v2i.yolov11",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/o",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/plant_3.v2i.yolov11",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/Rec",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/SavorGH",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/shopping_cart",
        "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/shopping_items",
    ]

    # Output folder for the new combined dataset
    output_base_path = "/mnt/home2/SU2/ingredients_photo_dataset/final_dataset/"
    # Rewrite labels to a specific new label (0 or 1)
    new_label = 0

    combine_datasets(base_paths, output_base_path, new_label)
    create_yaml_file(output_base_path)
