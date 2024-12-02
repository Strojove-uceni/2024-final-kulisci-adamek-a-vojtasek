import os
import cv2
from project.recipe_dataset.ingredients_functions import load_ingredients
from clip_model import ClipModel
composite_ingredients, single_ingredients = load_ingredients("../../recipe_dataset/ingredients_configs/ingredients_config.yaml")

ingredients = composite_ingredients + single_ingredients
clip_model = ClipModel()

clip_model.load_label_embeddings("./embedded_labels")
quit()
clip_model.save_embedded_lables("./embedded_labels")
input_folder = "../results/yolo_objects_cropped"

output_folder = "labeled_images"
os.makedirs(output_folder, exist_ok=True)

# Iterate over all files in the folder
for file_name in os.listdir(input_folder):
    if file_name.endswith(".jpg"):  # Process only .jpg files
        image_path = os.path.join(input_folder, file_name)

        # Load the image
        image = cv2.imread(image_path)

        # Generate a label for the image
        label = clip_model.label_image(image_path)
        # Overlay label text on the image
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color = (0, 255, 0)  # Green color
        thickness = 2
        org = (50, 50)  # Position (x, y) for the label

        # Put the text on the image
        labeled_image = cv2.putText(image, label, org, font, font_scale, font_color, thickness, cv2.LINE_AA)

        # Display the image
        cv2.imshow("Labeled Image", labeled_image)

        # Save the labeled image
        output_path = os.path.join(output_folder, file_name)
        cv2.imwrite(output_path, labeled_image)

        # Wait for a key press and close the display window
        if cv2.waitKey(0) & 0xFF == ord("q"):
            break

cv2.destroyAllWindows()
print(f"Labeled images saved in {output_folder}")