import abc as abc
import json
import os
import warnings
from collections import defaultdict
from typing import List, Any

import numpy as np
import torch
from PIL import Image
from tqdm import tqdm
import project.paths as paths

# define the embedding model abstract class that uses abc module
class EmbeddingModel(abc.ABC):
    """
    Abstract base class for embedding models.
    Keep in mind to implement _preprocess_image(), _embed_image() and _embed_label() for each child class
    Attributes:
        device (str): The device to run the model on, default device - cuda (if available).
        _track_embeddings (defaultdict): A dictionary to store track embeddings.
        _label_embeddings (list): A list to store label embeddings.
        tracks_embedded (bool): A flag indicating if tracks have been embedded.
        labels_embedded (bool): A flag indicating if labels have been embedded.
    """
    def __init__(self):
        """
        Initializes the EmbeddingModel with default values.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._track_embeddings = defaultdict(list)
        self._label_embeddings = {}
        self.tracks_embedded = False
        self.labels_embedded = False
    @abc.abstractmethod
    def _preprocess_image(self, image: Image) -> Image:
        """
        Abstract method to preprocess an image.

        Args:
            image (Image): The input image to preprocess.

        Returns:
            Image: The preprocessed image.
        """
        pass

    @abc.abstractmethod
    def _embed_image(self, image: Image) -> np.ndarray:
        pass

    @abc.abstractmethod
    def _embed_label(self, label: str) -> np.ndarray:
        pass

    def embed_image(self, image_path):
        return self._embed_image(self._preprocess_image(Image.open(image_path)))

    def embed_tracks(self, image_folder: str, strategy: str|None=None, output_folder: str|None =None):
        """
        :param image_folder: str path to your image folder,
            where each file is named {frame_num}_{track_id}.jpg/.jpeg/.png.
        :param output_folder: if provided automatically save tracks to output_folder in JSON.
                Could also be done manually by calling save_track_embeddings(output_folder)
        :param strategy: in future this param will decide what embedding strategy to pursue
        """
        if not os.path.exists(image_folder):
            print(f"Error: Image folder '{image_folder}' does not exist.")
            return

        image_files = [f for f in os.listdir(image_folder) if f.endswith((".jpg", ".jpeg", ".png"))]

        if not image_files:
            print(f"Error: Image folder '{image_folder}' is empty.")
            return
        for filename in tqdm(image_files, desc="Processing images"):
            image_path = os.path.join(image_folder, filename)
            try:
                frame_num, track_id = filename.split('_')
                track_id = track_id.split('.')[0]
            except ValueError:
                print(f"Skipping invalid file format: {filename}")
                continue
            image_embedding = self.embed_image(image_path)
            self._track_embeddings[track_id].append(image_embedding.tolist())
        self.tracks_embedded = True
        if output_folder is not None:
            self.save_track_embeddings(output_folder)

    def embed_labels(self, labels: List[str]):
        """
        Embeds a list of labels.
        Args:
            labels (List[str]): The list of labels to embed.
        """
        for label in tqdm(labels, desc="Calculating label embeddings"):
            embed_label = self._embed_label(label)
            self._label_embeddings[label] = embed_label
        self.labels_embedded = True

    def get_labels(self) -> np.ndarray:
        """
        Retrieves the label embeddings.

        Returns:
            np.ndarray: The array of label embeddings.
        """
        if not self.labels_embedded:
            print("Error: No label embeddings available. Call embed_labels() first.")
            return np.array([])
        return np.array(self._label_embeddings.keys)

    def get_track_embeddings(self) -> defaultdict[Any, list]:
        """
        Retrieves the track embeddings.

        Returns:
            defaultdict[Any, list]: The dictionary of track embeddings.
        """
        if not self.tracks_embedded and not self._track_embeddings:
            print("Error: No track embeddings available. Call embed_tracks() or load_track_embeddings() first.")
        return self._track_embeddings

    def save_track_embeddings(self, output_folder: str):
        """
        Saves the track embeddings to the specified folder.

        Args:
            output_folder (str): The folder to save the embeddings to.
        """
        # Ensure the output folder exists or create it
        os.makedirs(output_folder, exist_ok=True)

        if not self.tracks_embedded and not self._track_embeddings:
            print(
                "Error: No embeddings to save. Ensure tracks were embedded or loaded before calling save_track_embeddings().")
            return

        try:
            for track_id, embeddings in self._track_embeddings.items():
                output_path = os.path.join(output_folder, f"{track_id}_embeddings.json")
                with open(output_path, 'w') as file:
                    json.dump(embeddings, file)
            print(f"Embeddings saved successfully in {output_folder}.")
        except (OSError, IOError) as e:
            print(f"Error saving embeddings: {e}")

    def load_track_embeddings(self, input_folder: str):
        """
        Loads track embeddings from the specified folder.

        Args:
            input_folder (str): The folder to load the embeddings from.
        """
        if not os.path.exists(input_folder):
            print(f"Error: Input folder '{input_folder}' does not exist.")
            return

        self._track_embeddings.clear()

        try:
            for file_name in os.listdir(input_folder):
                if file_name.endswith(".json"):

                    track_id = file_name.split("_embeddings.json")[0]
                    file_path = os.path.join(input_folder, file_name)
                    with open(file_path, 'r') as file:
                        embeddings = json.load(file)

                        # Check if the embeddings are empty
                        if not embeddings:
                            warnings.warn(f"Warning: Track {track_id} in file '{file_name}' has empty embeddings.")

                        self._track_embeddings[track_id] = embeddings

            if self._track_embeddings:
                print(f"Embeddings loaded successfully from '{input_folder}'.")
                self.tracks_embedded = True
            else:
                print(f"Warning: No valid embeddings were loaded from '{input_folder}'.")
        except (OSError, IOError, json.JSONDecodeError) as e:
            print(f"Error loading embeddings: {e}")

    @staticmethod
    def cosine_distance(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Computes the cosine distance between two embeddings.

        Args:
            embedding1 (np.ndarray): The first embedding vector.
            embedding2 (np.ndarray): The second embedding vector.

        Returns:
            float: The cosine distance between the two embeddings.
        """
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        return 1 - (dot_product / (norm1 * norm2))

    def rank_tracks_by_similarity(self, label: str | np.ndarray, method: str = "average") -> list:
        """
        Ranks all track IDs by their similarity to a given label embedding.

        Args:
            label (str | np.ndarray): The text prompt (string) or precomputed label embedding (numpy array).
            method (str): The method to summarize distances across frames. Options: 'average', 'max'.

        Returns:
            list: A list of tuples (track_id, distance) ordered by the best match (lowest distance).
        """
        if not self._track_embeddings and self.tracks_embedded:
            print("Error: No track embeddings available. Ensure embeddings are loaded or generated.")
            return []

        # Embed the label if it's a string
        if isinstance(label, str):
            label_embedding = self._embed_label(label)
        elif isinstance(label, np.ndarray):
            label_embedding = label
        else:
            raise ValueError("Label must be a string (text prompt) or a numpy array (precomputed embedding).")

        # Compute the distance for each track
        ranked_tracks = []
        for track_id, embeddings in self._track_embeddings.items():
            # Compute distances for all frames in the track
            distances = np.asarray([self.cosine_distance(np.array(frame_embedding), label_embedding) for frame_embedding in
                         embeddings])

            # Summarize distance based on the method
            if method == "average":
                summarized_distance = np.mean(distances)
            elif method == "max":
                summarized_distance = np.max(distances)
            else:
                raise ValueError("Invalid method. Choose 'average' or 'max'.")

            ranked_tracks.append((track_id, summarized_distance))

        # Sort tracks by ascending distance (best match first)
        ranked_tracks.sort(key=lambda x: x[1])

        return ranked_tracks

    def assign_labels_to_tracks(self, labels: List[str], aggregation_method: str = "average") -> dict:
        """
        Assigns the best-matching label to each track based on the chosen aggregation method.

        Args:
            labels (List[str]): List of possible labels to assign.
            aggregation_method (str): The method to aggregate distances ('average' or 'max').

        Returns:
            dict: A dictionary mapping each track_id to its best-matching label.
        """
        if not self._track_embeddings:
            print("Error: No track embeddings available. Ensure embeddings are loaded or generated.")
            return {}

        if not self.labels_embedded:
            self.embed_labels(labels)

        track_labels = {}
        for track_id, embeddings in self._track_embeddings.items():
            avg_embedding = np.mean(embeddings, axis=0)
            distances = np.asarray([
                self.cosine_distance(avg_embedding, label_emb) for label_emb in self._label_embeddings
            ])

            # Aggregate distances using the chosen method
            if aggregation_method == "average":
                aggregated_distance = np.mean(distances)
            elif aggregation_method == "max":
                aggregated_distance = np.max(distances)
            else:
                raise ValueError("Invalid aggregation method. Choose 'average' or 'max'.")

            best_label_index = np.argmin(distances)
            best_label = labels[best_label_index]
            track_labels[track_id] = best_label

        return track_labels
    def label_image(self, image_path: str) -> str:
        """
        """

        image_embedding = self.embed_image(image_path)
        distances = [self.cosine_distance(image_embedding, label_emb) for label_emb in self._label_embeddings.values()]
        best_label_index = np.argmin(distances)
        best_label = list(self._label_embeddings.keys())[best_label_index]

        return best_label


# TODO: add following functionality in the future

    # def _embed_images_batch(self, images: List[Image]) -> np.ndarray:
    #     images = [self._preprocess_image(image) for image in images]
    #     inputs = self.processor(images=images, return_tensors="pt", padding=True).to(self.device)
    #     with torch.no_grad():
    #         image_features = self.model.get_image_features(**inputs)
    #     return image_features.cpu().numpy()

# # Výpočet nejlepšího labelu na základě průměrné vzdálenosti ke clusteru
# track_labels = {}
# for track_id, embeddings in track_embeddings.items():
#     avg_embedding = np.mean(embeddings, axis=0)
#
#     # Vypočti průměrné kosinové vzdálenosti mezi průměrným embeddingem a všemi label embeddings
#     distances = np.array([1 - np.dot(avg_embedding, label_emb) /
#                           (np.linalg.norm(avg_embedding) * np.linalg.norm(label_emb))
#                           for label_emb in label_embeddings])
#
#     # Najdi index nejbližšího labelu a přiřaď ho track_id
#     best_label_index = np.argmin(distances)
#     best_label = labels[best_label_index]
#     track_labels[track_id] = best_label

# # Uložení výsledků do result.txt a anotovaných obrázků do selected_images
# output_file = "/mnt/home2/UTIA/datasets/job_164/result.txt"
#
# with open(output_file, "w") as f:
#     for track_id in sorted(track_labels.keys(), key=lambda x: int(x)):
#         label = track_labels[track_id]
#         f.write(f"{track_id}: {label}\n")
#
#         # Najdi první dostupný obrázek pro track_id
#         first_image_path = next((os.path.join(cropped_images_folder, img)
#                                  for img in image_files if img.split('_')[1].split('.')[0] == track_id), None)
#
#         if first_image_path:
#             first_image = Image.open(first_image_path).resize((300, 300))
#
#             # Přidání textu s predikovaným labelm
#             draw = ImageDraw.Draw(first_image)
#             font = ImageFont.load_default()
#             text = f"{label} (Track ID: {track_id})"
#             text_position = (10, 10)
#             draw.text(text_position, text, fill="white", font=font)
#
#             # Ulož obrázek s textem do složky selected_images
#             first_image.save(os.path.join(output_folder, f"{track_id}.jpg"))
#
# print(f"Results saved to {output_file} and images saved to {output_folder}")
