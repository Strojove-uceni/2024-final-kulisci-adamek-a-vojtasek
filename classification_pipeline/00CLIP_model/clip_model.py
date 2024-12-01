from embedding_model import EmbeddingModel
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