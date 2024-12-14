import json

# Load the two COCO files
with (open('/home/petr/Documents/SU2_project/project/coco_dataset1/annotations/instances_relabelled.json', 'r') as file1,
      open('/home/petr/Documents/SU2_project/project/coco_dataset2/annotations/instances_relabelled2.json', 'r') as file2):
    coco1 = json.load(file1)
    coco2 = json.load(file2)


# Function to merge two COCO-like JSONs
def merge_coco_files_with_unique_ids(coco1, coco2):
    merged_coco = {
        'licenses': coco1.get('licenses', []) + [lic for lic in coco2.get('licenses', []) if
                                                 lic not in coco1.get('licenses', [])],
        'info': coco1.get('info', {}),
        'categories': coco1.get('categories', []),
        'images': [],
        'annotations': []
    }

    # Merge categories
    category_name_to_id = {category['name']: category['id'] for category in merged_coco['categories']}
    max_category_id = max(category_name_to_id.values()) if category_name_to_id else 0

    for category in coco2.get('categories', []):
        if category['name'] not in category_name_to_id:
            max_category_id += 1
            new_category = {**category, 'id': max_category_id}
            merged_coco['categories'].append(new_category)
            category_name_to_id[category['name']] = max_category_id

    # Merge images
    max_image_id = max(image['id'] for image in coco1.get('images', [])) if coco1.get('images', []) else 0
    image_id_mapping = {}  # Map old image ids to new image ids

    for image in coco1.get('images', []):
        image_id_mapping[image['id']] = image['id']  # Keep the existing mapping
        merged_coco['images'].append(image)

    for image in coco2.get('images', []):
        max_image_id += 1
        new_image = {**image, 'id': max_image_id}
        image_id_mapping[image['id']] = max_image_id  # Update mapping to new ID
        merged_coco['images'].append(new_image)

    # Merge annotations
    max_annotation_id = max(annotation['id'] for annotation in coco1.get('annotations', [])) if coco1.get('annotations',
                                                                                                          []) else 0

    for annotation in coco1.get('annotations', []):
        merged_coco['annotations'].append(annotation)  # Keep annotations from coco1 as is

    for annotation in coco2.get('annotations', []):
        max_annotation_id += 1
        new_annotation = {**annotation, 'id': max_annotation_id}

        # Update image_id to match the new image id in merged_coco
        if annotation['image_id'] in image_id_mapping:
            new_annotation['image_id'] = image_id_mapping[annotation['image_id']]

        # Update category_id to match the new category id in merged_coco
        if annotation['category_id'] in category_name_to_id.values():
            new_annotation['category_id'] = annotation['category_id']

        merged_coco['annotations'].append(new_annotation)

    return merged_coco


# Merge the COCO files ensuring distinct IDs
merged_coco = merge_coco_files_with_unique_ids(coco1, coco2)

# Save the merged COCO file
output_path = '/project/results/annotations/validation.json'
with open(output_path, 'w') as output_file:
    json.dump(merged_coco, output_file)