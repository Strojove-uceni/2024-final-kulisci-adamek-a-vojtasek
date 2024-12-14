import os
import shutil


def merge_image_folders(folder1, folder2, output_folder):
    """
    Merges two image folders into a single output folder.

    Parameters:
    -----------
    folder1 : str
        Path to the first folder containing images.
    folder2 : str
        Path to the second folder containing images.
    output_folder : str
        Path to the output folder where merged images will be saved.
    """
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get a list of all images in the output folder to avoid duplicates
    existing_files = set(os.listdir(output_folder))
    unique_id = 0  # To ensure unique filenames in case of collision

    def copy_images_from_folder(folder_path):
        """Copies images from a folder to the output folder with unique filenames."""
        nonlocal unique_id
        for file_name in os.listdir(folder_path):
            # Get the full path of the image
            src_path = os.path.join(folder_path, file_name)

            # Check if the path is actually a file (not a folder)
            if not os.path.isfile(src_path):
                continue

            # Extract the file extension
            file_ext = os.path.splitext(file_name)[-1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']:  # Check for image file types
                continue

            # Check for file name collision
            if file_name in existing_files:
                # Rename the file with a unique identifier
                new_file_name = f"{os.path.splitext(file_name)[0]}_{unique_id}{file_ext}"
                unique_id += 1
            else:
                new_file_name = file_name

            # Add the new file name to the existing files set
            existing_files.add(new_file_name)

            # Copy the file to the output folder
            dest_path = os.path.join(output_folder, new_file_name)
            shutil.copy2(src_path, dest_path)  # Use copy2 to preserve metadata

            print(f"Copied: {src_path} → {dest_path}")

    # Copy images from both folders
    copy_images_from_folder(folder1)
    copy_images_from_folder(folder2)

    print(f"\nMerging complete. Merged images are stored in: {output_folder}")


# Example usage
if __name__ == "__main__":
    folder1 = '/home/petr/Documents/SU2_project/project/classification_pipeline/images'
    folder2 = '/home/petr/Documents/SU2_project/project/coco_dataset2/images'
    output_folder = '/home/petr/Documents/SU2_project/project/merged_images'

    merge_image_folders(folder1, folder2, output_folder)