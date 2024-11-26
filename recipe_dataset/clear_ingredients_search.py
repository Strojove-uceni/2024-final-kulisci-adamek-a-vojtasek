import re

import yaml

from project.recipe_dataset.ingredient_class import Ingredient

def match_singular_or_plural(word, ingredient_list):
    """
    Match a word with its singular or plural form in the ingredient list.
    """
    for ingredient in ingredient_list:
        # Create regex to match singular and plural forms
        plural_pattern = rf"\b{ingredient}(es|s)?\b"
        if re.search(plural_pattern, word):
            return ingredient
    return None  # No match found

def extract_ingredient(raw_ingredient, composite_ingredients, single_ingredients):
    """
    Extract the core ingredient by prioritizing composites over singles,
    accounting for singular and plural forms.
    """
    raw = raw_ingredient.lower()

    # First, check for composite matches (with singular/plural logic)
    for composite in composite_ingredients:
        if match_singular_or_plural(raw, [composite]):
            return composite

    # Fallback to single ingredient matches (with singular/plural logic)
    for single in single_ingredients:
        if match_singular_or_plural(raw, [single]):
            return single

    return None  # If no match is found


# Define stopwords and styles
def load_ingredients(file_path):
    """
    Load categorized ingredients from YAML.
    """
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    # Extract categorized ingredients
    categories = data["categories"]

    # Flatten into composite and single ingredients
    composite_ingredients = []
    single_ingredients = []
    for category, items in categories.items():
        for item in items:
            if " " in item:  # Check for composite ingredients
                composite_ingredients.append(item)
            else:
                single_ingredients.append(item)

    return composite_ingredients, single_ingredients

# Access the lists
composite_ingredients, single_ingredients = load_ingredients("ingredients_configs/ingredients_config.yaml")

with open("data_cropped.yaml", "r") as file:
    dataset = yaml.safe_load(file)


for i in range(30, 60):
    ingredients = dataset[i]["ingredients"]
    for ing in ingredients:
        core_ingredient = extract_ingredient(ing, composite_ingredients, single_ingredients)
        print(f"FROM:    {ing}     =>     TO:    {core_ingredient}")
        print()
