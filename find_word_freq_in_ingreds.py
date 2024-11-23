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
    words = []
    for ingredient in ingredient_list:
        words.extend(ingredient.lower().split())  # Split into words and convert to lowercase
    return Counter(words)

# File path (update this to your actual path)
file_path = "data.yaml"

# Extract and analyze ingredients
all_ingredients = extract_ingredients(file_path)

# Analyze word frequency
word_freq = analyze_ingredients(all_ingredients)

# Display most common words
print("Most Common Words in Ingredients:")
for word, count in word_freq.most_common(50):  # Adjust number as needed
    print(f"{word}: {count}")

# Optional: Save the word frequency to a file
with open("word_frequency.txt", "w") as file:
    for word, count in word_freq.most_common():
        file.write(f"{word}: {count}\n")
