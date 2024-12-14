import os
import shutil

from tqdm import tqdm

from project.classification_pipeline.clip_model_pipeline.embedding_model import EmbeddingModel
import numpy as np
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel


# define the clip model class that inherits from the embedding model class
class ClipModel(EmbeddingModel):
    """
        A class is a wrapper for a CLIP Model. Inherits from EmbeddingModel

        Attributes:
            model (CLIPModel): The CLIP model used for generating embeddings.
            processor (CLIPProcessor): The processor used for preprocessing images and labels.
            device (str): The device to run the model on, default device - cuda (if available).

        Methods:
            _preprocess_image(image: Image) -> Image:
                Resizes the input image to the required dimensions for the CLIP model.
            _embed_image(image: Image) -> np.ndarray:
                Generates an embedding for the input image.
            _embed_label(label: str) -> np.ndarray:
                Generates an embedding for the input label.
        """
    def __init__(self, model_name: str = "openai/clip-vit-large-patch14"):
        """
        Initializes the ClipModel with the specified model name.

        Args:
            model_name (str): The name of the pre-trained CLIP model to use. default: clip-vit-large-patch14
        """
        super().__init__()
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def _preprocess_image(self, image: Image) -> Image:
        """
        Resizes the input image to the required dimensions for the CLIP model.

        Args:
            image (Image): The input image to preprocess.

        Returns:
            Image: The resized image.
        """
        return image.resize((224, 224))  # Resize for CLIP

    def _embed_image(self, image: Image) -> np.ndarray:
        """
        Generates an embedding for the input image.

        Args:
            image (Image): The input image to embed.

        Returns:
            np.ndarray: The embedding of the image.
        """
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        return image_features.cpu().numpy().flatten()

    def save_embedded_labels(self, output_folder: str):
        """
        Saves the track embeddings to the specified folder.

        Args:
            output_folder (str): The folder to save the embeddings to.
        """
        # Ensure the output folder exists or create it
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder, exist_ok=True)

        if not self.labels_embedded and not self._label_embeddings:
            print(
                "Error: No embeddings to save. Ensure labels were embedded or loaded before calling save_track_embeddings().")
            return

        try:
            for label, embeddings in self._label_embeddings.items():
                output_path = os.path.join(output_folder, f"{label}_embeddings.npy")
                np.save(output_path, embeddings)
            print(f"Embeddings saved successfully in {output_folder}.")
        except (OSError, IOError) as e:
            print(f"Error saving embeddings: {e}")

    def load_label_embeddings(self, input_folder):
        for file in tqdm(os.listdir(input_folder), desc="Loading label embeddings"):
            file_path = os.path.join(input_folder, file)
            if os.path.isfile(file_path) and file.endswith("_embeddings.npy"):
                try:
                    embeddings = np.load(file_path)
                    label = "_".join(file.split("_")[:-1])  # More robust label extraction
                    self._label_embeddings[label] = embeddings
                except (OSError, IOError) as e:
                    print(f"Error loading file {file}: {e}")
    def _embed_label(self, label: str) -> np.ndarray:
        """
        Generates an embedding for the input label.

        Args:
            label (str): The input label to embed.

        Returns:
            np.ndarray: The embedding of the label.
        """
        inputs = self.processor(text=[label], return_tensors="pt").to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        return text_features.cpu().numpy().flatten()