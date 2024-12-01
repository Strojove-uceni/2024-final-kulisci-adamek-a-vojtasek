
import yaml

from project.recipe_dataset.ingredients_functions import extract_ingredient, load_ingredients

composite_ingredients, single_ingredients = load_ingredients("ingredients_configs/ingredients_config.yaml")

with open("data_cropped.yaml", "r") as file:
    dataset = yaml.safe_load(file)


for i in range(30, 60):
    ingredients = dataset[i]["ingredients"]
    for ing in ingredients:
        core_ingredient = extract_ingredient(ing, composite_ingredients, single_ingredients)
        print(f"FROM:{ing}=>TO: {core_ingredient}")
        print()
