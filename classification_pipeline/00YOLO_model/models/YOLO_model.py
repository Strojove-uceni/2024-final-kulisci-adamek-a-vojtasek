import abc
from ultralytics import YOLO


class YoloModel(abc.ABC):
    def __init__(self, path_to_model:str = None):
        if not path_to_model:
            self.model = YOLO("models/for_vegetables.pt")