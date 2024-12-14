import yaml

from project import paths

# Load the ingredients configuration file
file_path = paths.config["ingredients_dict"]

# Read and parse the YAML file
with open(file_path, 'r', encoding='utf-8') as file:
    ingredients_config = yaml.safe_load(file)

# Create a reverse dictionary
reverse_dict = {}
for category, ingredients in ingredients_config.items():
    for key, values in ingredients.items():
        for value in values:
            reverse_dict[value] = key

# Display the first 20 entries of the reverse dictionary as a sample
print(len(reverse_dict))
sample_reverse_dict = dict(list(reverse_dict.items()))
print(len(set(sample_reverse_dict.values())))
with open(paths.config["reversed_ingredients_dict"], "w") as f:
    yaml.dump(sample_reverse_dict, f)

