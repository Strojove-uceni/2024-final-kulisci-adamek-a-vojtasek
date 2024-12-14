import yaml
import re

# Define quantity-related keywords and regex for fractions/numbers

quantity_pattern = re.compile(r"\d+|\d+/\d+")

# Initialize sets for unique quantities and ingredients
unique_quantities = set()
unique_ingredients = set()

# Function to classify terms and extract unique quantities and ingredients
def extract_unique_terms(ingredient):
    tokens = ingredient.lower().split()
    quantities = []
    actual_ingredients = []
    for token in tokens:
        if token in quantity_keywords or quantity_pattern.match(token):
            quantities.append(token)
        else:
            actual_ingredients.append(token)
    if quantities:
        unique_quantities.add(" ".join(quantities))
    if actual_ingredients:
        unique_ingredients.add(" ".join(actual_ingredients))

# Load and process the YAML file
file_path = "data.yaml"  # Update with the correct file path
with open(file_path, "r") as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
    for entry in data:
        if isinstance(entry, dict) and "ingredients" in entry:
            for ingredient in entry["ingredients"]:
                extract_unique_terms(ingredient)

# Print the counts
print(f"Number of unique quantities: {len(unique_quantities)}")
print(f"Number of unique ingredients: {len(unique_ingredients)}")

# Optional: Save unique terms for further review
with open("../ingredients_configs/unique_quantities.txt", "w") as file:
    file.write("\n".join(sorted(unique_quantities)))

with open("../ingredients_configs/unique_ingredients.txt", "w") as file:
    file.write("\n".join(sorted(unique_ingredients)))
