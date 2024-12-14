import json


def validate_coco_file(coco_file_path, log_path=None):
    """
    Validate that a COCO file has valid image IDs, category IDs, and annotations.

    Args:
        coco_file_path (str): Path to the COCO JSON file to validate.
        log_path (str, optional): If provided, logs the issues to this file.

    Returns:
        None
    """
    issues = []  # List to store validation issues

    # Step 1: Load the COCO file
    try:
        with open(coco_file_path, 'r') as f:
            coco_data = json.load(f)
    except Exception as e:
        print(f"Error: Failed to load COCO file. {e}")
        return

    # Step 2: Extract essential data
    images = coco_data.get('images', [])
    annotations = coco_data.get('annotations', [])
    categories = coco_data.get('categories', [])

    # Create mappings for quick lookup
    image_ids = {image['id'] for image in images}
    category_ids = {category['id'] for category in categories}
    category_names = {category['id']: category['name'] for category in categories}

    print(f"Total images: {len(images)}")
    print(f"Total annotations: {len(annotations)}")
    print(f"Total categories: {len(categories)}")

    # Step 3: Validate each annotation
    for i, annotation in enumerate(annotations):
        annotation_id = annotation.get('id')
        image_id = annotation.get('image_id')
        category_id = annotation.get('category_id')
        bbox = annotation.get('bbox')

        if annotation_id is None:
            issues.append(f"Annotation {i}: Missing 'id' field.")

        if image_id not in image_ids:
            issues.append(
                f"Annotation {i} (ID={annotation_id}): 'image_id' ({image_id}) does not exist in the image list.")

        if category_id not in category_ids:
            issues.append(
                f"Annotation {i} (ID={annotation_id}): 'category_id' ({category_id}) is not in the categories list.")

        if not isinstance(bbox, list) or len(bbox) != 4 or not all(isinstance(x, (int, float)) for x in bbox):
            issues.append(f"Annotation {i} (ID={annotation_id}): 'bbox' is invalid. Got {bbox}.")

    # Step 4: Validate images
    image_ids_seen = set()
    for i, image in enumerate(images):
        image_id = image.get('id')
        file_name = image.get('file_name')

        if image_id is None:
            issues.append(f"Image {i}: Missing 'id' field.")

        if image_id in image_ids_seen:
            issues.append(f"Image {i}: Duplicate image ID '{image_id}'.")
        else:
            image_ids_seen.add(image_id)

        if not isinstance(file_name, str) or len(file_name) == 0:
            issues.append(f"Image {i}: 'file_name' is missing or empty.")

    # Step 5: Validate categories
    category_ids_seen = set()
    for i, category in enumerate(categories):
        category_id = category.get('id')
        category_name = category.get('name')

        if category_id is None:
            issues.append(f"Category {i}: Missing 'id' field.")

        if category_id in category_ids_seen:
            issues.append(f"Category {i}: Duplicate category ID '{category_id}'.")
        else:
            category_ids_seen.add(category_id)

        if not isinstance(category_name, str) or len(category_name) == 0:
            issues.append(f"Category {i}: 'name' is missing or empty.")

    # Step 6: Print results
    if issues:
        print(f"Validation failed with {len(issues)} issues found.")
        for issue in issues:
            print(f"- {issue}")

        # Optionally, write issues to log file
        if log_path:
            with open(log_path, 'w') as log_file:
                log_file.write("\n".join(issues))
            print(f"Issues have been logged to: {log_path}")
    else:
        print("Validation Passed! The COCO file is valid.")


if __name__ == "__main__":
    # Path to the COCO file
    coco_file_path = "/home/petr/Documents/SU2_project/project/coco_dataset1/annotations/clip_results.json"

    # Optional log file to store issues

    # Validate the COCO file
    validate_coco_file(coco_file_path)
