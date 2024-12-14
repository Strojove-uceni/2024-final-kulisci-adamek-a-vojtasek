import yaml

from project import paths


def recipe_filtering(labels: list):
    labels_set = set(labels)
    with open(paths.config["recipe_dataset"]) as f:
        dataset = yaml.safe_load(f)
    for i in range(len(dataset)):
        ingredients = set(dataset[i]["ingredients"])
        if ingredients.issubset(labels_set):
            return dataset[i]["directions"]
    return None