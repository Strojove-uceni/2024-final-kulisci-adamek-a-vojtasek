
import yaml

from clip_model import ClipModel
import project.paths as paths
from project.recipe_dataset.ingredients_functions import load_ingredients

input_file = paths.config["ingredients_dict"]
composite_ingredients, single_ingredients = load_ingredients(input_file)

ingredients = composite_ingredients + single_ingredients
clip_model = ClipModel()

# clip_model.load_label_embeddings("./embedded_labels")
clip_model.embed_labels(ingredients)
clip_model.save_embedded_labels(paths.config["embedded_labels"])


