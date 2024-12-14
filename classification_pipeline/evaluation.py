import json
import os.path
from collections import defaultdict
import numpy as np


def map_image_and_category_ids(ground_truth_file, prediction_file):
    with open(ground_truth_file, 'r') as f:
        coco_gt = json.load(f)

    with open(prediction_file, 'r') as f:
        coco_preds = json.load(f)

    filename_to_id = {os.path.basename(image['file_name']): image['id'] for image in coco_gt['images']}
    category_name_to_id = {category['name']: category['id'] for category in coco_gt['categories']}
    category_id_to_name = {category['id']: category['name'] for category in coco_preds['categories']}

    for pred in coco_preds['annotations']:
        image_filename = next((os.path.basename(img['file_name']) for img in coco_preds['images'] if img['id'] == pred['image_id']), None)
        if image_filename in filename_to_id:
            pred['image_id'] = filename_to_id[image_filename]

        category_name = category_id_to_name.get(pred['category_id'])
        if category_name in category_name_to_id:
            pred['category_id'] = category_name_to_id[category_name]

    return coco_preds


def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def existance_pr(predictions, ground_truths, class_id, iou_threshold=0.5):
    """
    Calculate True Positives (TP), False Positives (FP), and False Negatives (FN)
    for the presence of an ingredient in an image, regardless of how many times it appears.

    Parameters:
    -----------
    predictions : list of dict
        List of predictions, each containing 'category_id', 'bbox', and 'image_id'.
    ground_truths : list of dict
        List of ground-truth annotations, each containing 'category_id', 'bbox', and 'image_id'.
    class_id : int
        The ID of the class (ingredient) to calculate precision and recall for.
    iou_threshold : float
        The IoU threshold for a prediction to be considered a correct match.

    Returns:
    --------
    tuple (int, int, int)
        The counts of True Positives (TP), False Positives (FP), and False Negatives (FN) for the given class.
    """
    # Count True Positives (TP)
    tp = 0
    gt_matched_ids = set()

    # Get all unique image_ids where the current class is in ground truth
    gt_images_with_class = {gt['image_id'] for gt in ground_truths if gt['category_id'] == class_id}
    pred_images_with_class = {pred['image_id'] for pred in predictions if pred['category_id'] == class_id}

    for image_id in pred_images_with_class:
        # Check if the predicted ingredient is present in the ground truth for this image
        gt_boxes = [gt['bbox'] for gt in ground_truths if gt['image_id'] == image_id and gt['category_id'] == class_id]
        pred_boxes = [pred['bbox'] for pred in predictions if pred['image_id'] == image_id and pred['category_id'] == class_id]

        # Check if any predicted box for this image matches any of the ground truth boxes
        match_found = False
        for pred_box in pred_boxes:
            for gt_box in gt_boxes:
                iou = calculate_iou(pred_box, gt_box)
                if iou >= iou_threshold:
                    match_found = True
                    break
            if match_found:
                break

        if match_found:
            tp += 1  # The ingredient is correctly detected for this image
            gt_matched_ids.add(image_id)  # Mark this ground-truth ingredient as matched

    # Count False Positives (FP)
    fp = 0
    for image_id in pred_images_with_class:
        if image_id not in gt_images_with_class:  # Ingredient predicted for an image where it doesn't exist
            fp += 1

    # Count False Negatives (FN)
    fn = 0
    for image_id in gt_images_with_class:
        if image_id not in pred_images_with_class:  # No prediction for this image where ground truth has the ingredient
            fn += 1
        elif image_id not in gt_matched_ids:  # Ground truth exists but no correct prediction with sufficient IoU
            fn += 1

    return tp, fp, fn

def calculate_precision_recall(predictions, ground_truths, class_id, iou_threshold=0.5):
    tp, fp, fn = 0, 0, 0
    gt_matched_ids = set()

    for pred in predictions:
        if pred['category_id'] != class_id:
            continue

        pred_box = pred['bbox']
        pred_image_id = pred['image_id']

        best_iou = 0
        best_id = None
        for gt in ground_truths:
            if gt['image_id'] != pred_image_id or gt['category_id'] != class_id:
                continue
            iou = calculate_iou(pred_box, gt['bbox'])
            if iou > best_iou:
                best_iou = iou
                best_id = gt['id']
        if best_iou >= iou_threshold:
            tp += 1
            gt_matched_ids.add(best_id)  # Mark ground-truth as matched
        else:
            fp += 1

    for gt in ground_truths:
        if gt['category_id'] == class_id and gt['id'] not in gt_matched_ids:
            fn += 1

    return tp, fp, fn


def calculate_map(ground_truth_file, prediction_file, iou_threshold=0.5, count_empty_classes=False):
    coco_preds = map_image_and_category_ids(ground_truth_file, prediction_file)

    with open(ground_truth_file, 'r') as f:
        coco_gt = json.load(f)

    predictions = coco_preds['annotations']
    ground_truths = coco_gt['annotations']
    classes = coco_gt['categories']

    precision_per_class = {}
    recall_per_class = {}

    for category in classes:
        class_id = category['id']
        class_name = category['name']

        class_ground_truths = [gt for gt in ground_truths if gt['category_id'] == class_id]

        if len(class_ground_truths) == 0:
            precision, recall = 0, 0
            print(f"Class '{class_name}' has no ground-truth annotations. Skipping AP and Recall calculation for this class.")
        else:
            tp, fp, fn = calculate_precision_recall(predictions, ground_truths, class_id, iou_threshold)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        precision_per_class[class_name] = precision
        recall_per_class[class_name] = recall

    if count_empty_classes:
        ap_score = sum(precision_per_class.values()) / len(precision_per_class)
        recall_score = sum(recall_per_class.values()) / len(recall_per_class)
    else:
        valid_classes = [ap for class_name, ap in precision_per_class.items() if ap is not None]
        if len(valid_classes) > 0:
            ap_score = sum(valid_classes) / len(valid_classes)
            recall_score = sum(recall_per_class.values()) / len(valid_classes)
        else:
            ap_score = 0
            recall_score = 0

    sorted_ap_per_class = dict(sorted(precision_per_class.items(), key=lambda item: item[1], reverse=True))

    print("\nP and R per class (sorted by P):")
    for class_name, ap in sorted_ap_per_class.items():
        recall = recall_per_class[class_name]
        print(f" - {class_name}: AP = {ap:.4f}, Recall = {recall:.4f}")

    print(f"\nP: {ap_score:.4f}, R: {recall_score:.4f}")
    return ap_score, recall_score

if __name__ == "__main__":
    # Paths to your COCO annotation files

    ground_truth_path = "/home/petr/Documents/SU2_project/project/coco_dataset1/annotations/instances_relabelled.json"
    prediction_path = "/home/petr/Documents/SU2_project/project/coco_dataset1/annotations/clip_results.json"

    # IoU threshold
    iou_thresholds = [0, 0.5, 0.75, 0.9] # This can be 0.5, 0.75, etc.

    # Calculate mAP
    for iou_threshold in iou_thresholds:
        map_score, mrecall_score = calculate_map(ground_truth_path, prediction_path, iou_threshold)
        print(f"mAP at IoU={iou_threshold}: {map_score:.4f}, mRecall at IoU={iou_threshold}: {mrecall_score:.4f}")