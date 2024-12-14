import json


def relabel_coco_categories(coco_file_path, output_path, custom_category_mapping):
    """
    Relabel and merge COCO categories based on a custom mapping.

    Args:
        coco_file_path (str): Path to the input COCO JSON file.
        output_path (str): Path where the updated COCO JSON file will be saved.
        custom_category_mapping (dict): Mapping of old category names to new category names.
                                        If the value is `None`, the category and its annotations will be removed.
                                        If the value is a new label, annotations will be relabeled to the new label.

    Returns:
        None
    """
    # Step 1: Load the COCO file
    with open(coco_file_path, 'r') as f:
        coco_data = json.load(f)

    # Step 2: Create a mapping for old category IDs to new category names
    old_category_id_to_name = {category['id']: category['name'] for category in coco_data['categories']}
    name_to_new_category = {name: new_name for name, new_name in custom_category_mapping.items() if
                            new_name is not None}
    categories_to_remove = {name for name, new_name in custom_category_mapping.items() if new_name is None}

    # Step 3: Create a new list of categories
    new_categories = {}
    new_category_id = 1  # Start category IDs from 1

    for old_category in coco_data['categories']:
        old_name = old_category['name']

        # Check if the category is in the mapping
        if old_name in categories_to_remove:
            continue  # Remove this category

        new_name = name_to_new_category.get(old_name, old_name)  # Rename or keep as is

        if new_name not in new_categories:
            new_categories[new_name] = new_category_id
            new_category_id += 1

    # Convert new categories into COCO format
    new_coco_categories = [{"id": id, "name": name} for name, id in new_categories.items()]

    # Step 4: Relabel and filter annotations
    new_annotations = []
    for annotation in coco_data['annotations']:
        old_category_id = annotation['category_id']
        old_category_name = old_category_id_to_name.get(old_category_id)

        # Skip if the category is meant to be removed
        if old_category_name in categories_to_remove:
            continue

        new_category_name = name_to_new_category.get(old_category_name, old_category_name)

        # Assign the new category_id
        new_category_id = new_categories.get(new_category_name)
        if new_category_id is None:
            print(f"Warning: Category '{new_category_name}' not found in new category list.")
            continue

        # Update annotation's category ID
        annotation['category_id'] = new_category_id
        new_annotations.append(annotation)

    # Step 5: Update COCO structure
    updated_coco_data = {
        "info": coco_data.get("info", {}),
        "licenses": coco_data.get("licenses", []),
        "images": coco_data['images'],  # Keep image information intact
        "annotations": new_annotations,  # Use updated annotations
        "categories": new_coco_categories  # Use updated categories
    }

    # Step 6: Save the updated COCO file
    with open(output_path, 'w') as f:
        json.dump(updated_coco_data, f, indent=4)

    print(f"Updated COCO file saved to {output_path}")


if __name__ == "__main__":
    # Path to the original COCO file


    # Custom mapping for merging and removing categories
    custom_category_mapping = {
        'apple cider vinegar': 'vinegar',
        'dry yeast': None,
        'fish sauce': None,
        'tabasco': 'hot sauce',
        'salt': None,
        'sriracha': 'hot sauce',
        'greek yogurt': 'yogurt',
        'kyprici prasek': 'baking powder',
        'pernikove koreni': 'gingerbread spice',
        'spaghetti': 'pasta',
        'chilli powder': 'chilli',
        'cornmeal': 'starch',
        'potato starch': 'starch',
        'pickle': 'pickles',
        'chicken breast': 'chicken',
        'chicken thigh': 'chicken',
        'mint': None,
        'argula': 'arugula',
        'kapr': None,
        'karp': None,
        'sourdough bread': 'bread',
        'white pepper': 'pepper',
        'quinoa': None,
        'black olive': 'olive',
        'pepper': None,
        'arugula': None,
        'red onion': 'onion',
        'white onion': 'onion',
        'shallot': 'onion',
        'soya': None,
        'cheese': None
    }
    ground_truth_path = "/project/results/annotations/validation.json"
    output_path = "/project/results/annotations/validation_relabeled.json"
    # prediction_path = "/project/coco_dataset1/annotations/instances_.json"
    # output_path = "/project/coco_dataset1/annotations/instances_relabelled_preds.json"
    # Call the function
    relabel_coco_categories(ground_truth_path, output_path, custom_category_mapping)
