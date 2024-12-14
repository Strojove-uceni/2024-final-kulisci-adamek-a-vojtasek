import json

from project import paths
from project.classification_pipeline.classifier import IngredientClassifier
from project.classification_pipeline.evaluation import calculate_pr

if "__name__" == "__main__":
    classifier = IngredientClassifier()
    ingreds = classifier.inference(['your image_path'])
