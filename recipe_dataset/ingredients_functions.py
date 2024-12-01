import yaml
import re

from project.recipe_dataset.ingredient_class import Ingredient

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

def match_singular_or_plural(raw, ingredient_list):
    """
    Match a word with its singular or plural form in the ingredient list using regex.
    """
    # Build regex pattern for both regular and irregular plurals
    patterns = []
    for ingredient in ingredient_list:
        # Add irregular plural rules directly to the regex
        if ingredient.endswith("y"):  # Words like "strawberry" -> "strawberries"
            patterns.append(rf"{ingredient[:-1]}(y|ies)")
        elif ingredient.endswith("o"):  # Words like "tomato" -> "tomatoes"
            patterns.append(rf"{ingredient}(e|)s")
        elif ingredient.endswith("f"):  # Words like "loaf" -> "loaves"
            patterns.append(rf"{ingredient[:-1]}(f|ves)")
        else:  # Regular plural forms (add 's' or 'es')
            patterns.append(rf"{ingredient}(es|s)?")

    # Combine all patterns into one regex
    combined_pattern = rf"\b({'|'.join(patterns)})\b"

    # Match against the raw string
    match = re.search(combined_pattern, raw)
    if match:
        return match.group(0)  # Return the matched ingredient

    return None  # No match found