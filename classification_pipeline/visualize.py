import json
import os
import cv2
import project.paths as paths
# Paths

# Load the COCO JSON
with open(paths.config["clip_results"], "r") as f:
    coco_data = json.load(f)

# Create a dictionary to map category_id to category name
category_dict = {category['id']: category['name'] for category in coco_data['categories']}


# Function to visualize a specific image with annotations
def visualize_image():
    image_path = coco_data["image"]["path"]

    # Check if the image exists
    if not os.path.exists(image_path):
        print(f"Image {image_path} does not exist.")
        return

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image {image_path}.")
        return

    # Draw all annotations related to this image
    for annotation in coco_data['annotations']:
        # Extract bounding box information (if available)
        bbox = annotation.get('bbox', None)
        category_id = annotation['category_id']
        label = category_dict[category_id]
        label_str = ""
        # i = 0
        # for label in label_list:
        #     if i > 0:
        #         label_str = label_str + ", "
        #     label_str += label
        #     i += 1
        # Draw the bounding box if available
        if bbox:
            x_min, y_min, width, height = bbox
            x_max, y_max = int(x_min + width), int(y_min + height)
            x_min, y_min = int(x_min), int(y_min)

            # Draw rectangle for bounding box
            color = (0, 255, 0)  # Green
            thickness = 2
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, thickness)

            # Draw label above the bounding box
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1
            label_position = (x_min, y_min - 10 if y_min - 10 > 10 else y_min + 10)
            cv2.putText(image, label, label_position, font, font_scale, color, font_thickness, cv2.LINE_AA)

# Display the labeled image
    cv2.imshow("Labeled Image", image)

    # Wait for a key press and close the display window
    if cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()


# Example usage to visualize image with a specific image_id
# Note: Replace the image_id below with the actual ID of the image you want to visualize
desired_image_id = 0  # Replace with the correct ID
visualize_image()
