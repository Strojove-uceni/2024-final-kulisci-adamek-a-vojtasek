
import yaml

from project.recipe_dataset.ingredients_functions import extract_ingredient, load_ingredients

composite_ingredients, single_ingredients = load_ingredients("../ingredients_configs/ingredients_config.yaml")

print(composite_ingredients, single_ingredients)
with open("data_cropped.yaml", "r") as file:
    dataset = yaml.safe_load(file)


for i in range(100, 200):
    ingredients = dataset[i]["ingredients"]
    none = "none"
    unable = False
    for ing in ingredients:
        core_ingredient = extract_ingredient(ing, composite_ingredients, single_ingredients)
        if core_ingredient is None:
            break
            unable = True

