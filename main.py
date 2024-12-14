import os
import shutil

from project import paths
from project.chatGPT_API.chatptapi import chat_gpt_api
from project.classification_pipeline.classifier import IngredientClassifier
from project.recipe_dataset.filtering import recipe_filtering

if __name__ == "__main__":
    classifier = IngredientClassifier()
    shutil.rmtree(paths.config["annotated_images"])
    os.makedirs(paths.config["annotated_images"], exist_ok=True)

    images, ingredients= classifier.inference(paths.config["images"])
    if images:
        for name, image in images.items():
            image.save(f"{paths.config["annotated_images"]}/{os.path.basename(name)}")
    # print("GPT recipe:")
    # print(chat_gpt_api(list(ingredients.values())[0]))
    print("Filtered recipe:")
    for i, line in enumerate(recipe_filtering(["chicken", "bread", "egg", "flour", "olive oil"]), start=1):
        print(f"{i})", line)
        print()