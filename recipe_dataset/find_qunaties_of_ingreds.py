import yaml
import re

# Define quantity-related keywords
quantity_keywords = {
    "cup", "cups", "tablespoon", "tablespoons", "teaspoon", "teaspoons", "ounce", "ounces",
    "pound", "pounds", "gram", "grams", "liter", "liters", "milliliter", "milliliters",
    "1/2", "1/4", "3/4", "1/3", "1/8", "kg", "ml", "tbsp", "tsp"
}

# Regex to identify fractions or numbers
quantity_pattern = re.compile(r"\d+|\d+/\d+")

# Function to classify terms
def classify_terms(ingredient):
    tokens = ingredient.lower().split()
    quantities = []
    actual_ingredients = []
    for token in tokens:
        if token in quantity_keywords or quantity_pattern.match(token):
            quantities.append(token)
        else:
            actual_ingredients.append(token)
    return " ".join(quantities), " ".join(actual_ingredients)

# Process the dataset
file_path = "data.yaml"  # Update with your file path

quantity_ingredient_pairs = []

with open(file_path, "r") as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
    for entry in data:
        if isinstance(entry, dict) and "ingredients" in entry:
            for ingredient in entry["ingredients"]:
                quantities, ingredient_core = classify_terms(ingredient)
                quantity_ingredient_pairs.append({quantities: ingredient_core})

# Save results to a single YAML file
output_file = "ingredients_configs/quantities_ingredients.yaml"
with open(output_file, "w") as file:
    yaml.dump(quantity_ingredient_pairs, file)

print(f"Quantities and ingredients saved to {output_file}.")
