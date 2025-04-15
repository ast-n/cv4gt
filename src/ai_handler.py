""" AI HANDLER """
""" This script should:
    - Handle setup and loading of AI models into memory.
    - Handle passing data directly to and from AI models.
    - Handle any mid-operation self-improvement or retraining systems."""

from huggingface_hub import hf_hub_download
from ultralytics import YOLO
import os


class ModelManager:
    def __init__(self):
        self.object_detection_model = None
        self.model_loaded = False

    def load_object_detection_model(self, model_path="models/YOLOv8-cv4gt-data-11-04_10e.pt"):
        """
        Loads a YOLO model from a local path.
        """
        try:
            if model_path and os.path.exists(model_path):
                self.object_detection_model = YOLO(model_path)
                self.model_loaded = True
                print(f"Model loaded from local path: {model_path}")
                return True
            else:
                raise FileNotFoundError(f"Model file not found at: {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    """   
    Broken rn 
    def download_model_from_huggingface(self):

        repo_id = "ast-n/cv4gt"
        filename = "YOLOv8-cv4gt-bad-dataset_epochs500.pt"

        model_path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir="models")
        return model_path

    """
    
    def detect_objects(self, image):
        """
        Runs object detection on an image
        """
        if not self.model_loaded:
            raise Exception("Model not loaded. Call load_object_detection first")
        
        results = self.object_detection_model(image)
        return results[0]
    
    def get_objects(self, image):
        """
        Returns detected objects and their bounding boxes
        """

        results = self.detect_objects(image)

        detections = []

        for box in results.boxes:
            class_id = int(box.cls)
            class_name = results.names[class_id]
            confidence = float(box.conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                'class': class_name,
                'confidence': confidence,
                'bbox': [x1, y1, x2, y2]
            })
        return detections

model_manager = ModelManager()

def load_object_detection_model(model_path="models/YOLOv8-cv4gt-data-11-04_10e.pt"):
    return model_manager.load_object_detection_model(model_path)

def get_objects(image):
    return model_manager.get_objects(image)

def load_bound_detector():
    return NotImplementedError

def get_bounds():
    return NotImplementedError

def self_improve():
    return NotImplementedError