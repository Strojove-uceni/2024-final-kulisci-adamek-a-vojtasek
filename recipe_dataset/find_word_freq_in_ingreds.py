import yaml
from collections import Counter

# Function to extract ingredients from a large YAML file
def extract_ingredients(file_path):
    ingredients = []
    with open(file_path, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)  # Load the full YAML
        for entry in data:
            if isinstance(entry, dict) and 'ingredients' in entry:  # Check for valid entry
                ingredients.extend(entry['ingredients'])
    return ingredients

# Analyze ingredients to find frequent words
def analyze_ingredients(ingredient_list):
    # Convert each ingredient to lowercase and remove duplicates
    unique_ingredients = [ingredient.lower().strip() for ingredient in set(ingredient_list)]
    # Count occurrences of each ingredient
    return Counter(unique_ingredients)

# File path (update this to your actual path)
file_path = "data_cropped.yaml"

# Extract and analyze ingredients
all_ingredients = extract_ingredients(file_path)

# Analyze word frequency
word_freq = analyze_ingredients(all_ingredients)

# Display most common words
print("Most Common Words in Ingredients:")
for word, count in word_freq.most_common(50):  # Adjust number as needed
    print(f"{word}: {count}")

# Optional: Save the word frequency to a file
with open("../ingredients_configs/ingredient_frequency.txt", "w") as file:
    for word, count in word_freq.most_common():
        file.write(f"{word}: {count}\n")
