
import yaml

from project.recipe_dataset.ingredients_functions import extract_ingredient, load_ingredients

composite_ingredients, single_ingredients = load_ingredients("ingredients_configs/ingredients_config.yaml")

with open("data_cropped.yaml", "r") as file:
    dataset = yaml.safe_load(file)


for i in range(100, 200):
    ingredients = dataset[i]["ingredients"]
    none = "none"
    for ing in ingredients:
        core_ingredient = extract_ingredient(ing, composite_ingredients, single_ingredients)
        if core_ingredient is not None:
            print(f"FROM: {ing:<50} => TO: {core_ingredient:<50}")  # Format with consistent spacing
        else:
            print(f"FROM: {ing:<50} => TO: {none:<50}")