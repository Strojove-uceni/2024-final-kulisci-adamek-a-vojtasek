import ast
import json

import pandas as pd


def filter_ingredients(ingredients_string, desired, expected):
    # Convert string representation of list to an actual list
    try:
        ingredients_list = ast.literal_eval(ingredients_string)  # Use ast.literal_eval for safety
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing ingredients: {ingredients_string}\nError: {e}")
        return False  # Return False if the format is incorrect

    # Ensure the recipe contains at least 5 ingredients
    if len(ingredients_list) < 5:
        return False

    # Convert each ingredient in the recipe list to lowercase for case-insensitive matching
    ingredients_list = [ingredient.lower().strip() for ingredient in ingredients_list]

    # Combine desired and expected ingredients
    combined_ingredients = expected | desired

    # Check if the ingredients in the recipe are a subset of the combined expected and desired ingredients
    is_subset = set(ingredients_list).issubset(combined_ingredients)

    # Ensure there is at least one ingredient from the desired set
    has_desired = any(ingredient in desired for ingredient in ingredients_list)

    # Return True if the recipe ingredients are a subset and contain at least one desired ingredient
    return is_subset and has_desired


# File paths
# file_path = '/mnt/home2/recipe_dataset/full_dataset.csv'
file_path = 'D:/Programovani/SU2/RecipeNLG_dataset.csv'
exp_ing_file = "expected_ingredients.json"
desired_ing_file = "desired_ingredients.json"

# Load data
try:
    df = pd.read_csv(file_path)
    print(f"Total recipes loaded: {len(df)}")
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")
    df = pd.DataFrame()

# Load expected and desired ingredients
try:
    with open(exp_ing_file, "r") as file:
        expected_ing = json.load(file)
    expected_ing = set(map(str.lower, expected_ing))

    with open(desired_ing_file, "r") as file:
        desired_ing = json.load(file)
    desired_ing = set(map(str.lower, desired_ing))
except FileNotFoundError as e:
    print(f"Error loading ingredient files: {e}")
    expected_ing = set()
    desired_ing = set()

# Proceed if data and ingredients are loaded successfully
if not df.empty and expected_ing and desired_ing:
    # Apply the function and filter rows
    try:
        filtered_mask = df['NER'].apply(filter_ingredients, args=(desired_ing, expected_ing))
        filtered_recipes = df[filtered_mask].reset_index(drop=True)

        # Print the filtered recipes
        columns = ["directions", "ingredients", "NER"]
        filtered_recipes_subset = filtered_recipes[columns] if not filtered_recipes.empty else pd.DataFrame()

        print(filtered_recipes_subset.head())
        print(f"Number of filtered recipes: {len(filtered_recipes_subset)}")
    except KeyError as e:
        print(f"Key error: {e}. Please check if the 'ingredients' column is correctly named.")
else:
    print("Either the data or ingredient lists could not be loaded successfully.")


