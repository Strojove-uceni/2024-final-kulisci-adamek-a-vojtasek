
import yaml

from project import paths
from project.recipe_dataset.ingredients_functions import extract_ingredient, load_ingredients

composite_ingredients, single_ingredients = load_ingredients("../ingredients_configs/ingredients_config.yaml")

with open("dataset_recipe_unified.yaml", "r") as file:
    dataset = yaml.safe_load(file)
with open(paths.config["reversed_ingredients_dict"]) as f:
    unified_labels = yaml.safe_load(f)
new_dataset = []
print(len(dataset))
for i in range(len(dataset)):
    ingredients = dataset[i]["ingredients"]
    new_ingreds = []
    for ing in ingredients:
        new_ingreds.append(unified_labels[extract_ingredient(ing, composite_ingredients, single_ingredients)])
    dataset[i]["ingredients"] = new_ingreds

with open("dataset_recipe_unified.yaml", "w") as f:
    yaml.dump(dataset, f)

