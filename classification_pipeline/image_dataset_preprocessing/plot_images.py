import os
import glob
import cv2
import matplotlib.pyplot as plt


def plot_image_with_bboxes(image_path, label_path):
    """
    Plot an image with its bounding boxes.
    """
    # Load the image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for plotting

    # Read the label file
    with open(label_path, 'r') as file:
        lines = file.readlines()

    # Iterate over each bounding box
    bboxes = []
    for line in lines:
        elements = line.strip().split()
        class_id = elements[0]
        bbox = list(map(float, elements[1:]))  # (x_center, y_center, width, height)

        # Convert bbox from xywh to x1, y1, x2, y2 for drawing
        x_center, y_center, width, height = bbox
        print(image.shape)
        x1 = int((x_center - width / 2.0) * image.shape[1])
        y1 = int((y_center - height / 2.0) * image.shape[0])
        x2 = int((x_center + width / 2.0) * image.shape[1])
        y2 = int((y_center + height / 2.0) * image.shape[0])

        # Append bounding box for drawing later
        bboxes.append((x1, y1, x2, y2, class_id))

    # Draw all bounding boxes
    for x1, y1, x2, y2, class_id in bboxes:
        cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(image, f'Class {class_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    # Plot the image
    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    plt.axis('off')
    plt.show()


def plot_images_from_folder(image_folder, label_folder):
    """
    Plot images with bounding boxes from given image and label folders.
    """
    image_files = glob.glob(os.path.join(image_folder, '*.jpg'))
    i = 0
    for image_file in image_files:
        # Construct the corresponding label file path
        label_file = os.path.join(label_folder, os.path.basename(image_file).replace('.jpg', '.txt'))
        print(image_file)
        if os.path.exists(label_file):
            plot_image_with_bboxes(image_file, label_file)
        else:
            print(f"Warning: Label file for {image_file} does not exist.")
            continue
        i += 1
        if i >= 5:
            break
def main():
    base_path = "/mnt/home2/SU2/ingredients_photo_dataset/all_old_ds/Vegetables.v1i.yolov11"
    subsets = ["train", "val", "test"]

    for subset in subsets:
        image_folder = os.path.join(base_path, subset, 'images')
        label_folder = os.path.join(base_path, subset, 'labels')

        if os.path.exists(image_folder) and os.path.exists(label_folder):
            plot_images_from_folder(image_folder, label_folder)
        else:
            print(f"Warning: Folder {image_folder} or {label_folder} does not exist.")


if __name__ == "__main__":
    main()
