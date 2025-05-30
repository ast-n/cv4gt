""" AI HANDLER
This script should:
    - Handle setup and loading of AI models into memory.
    - Handle passing data directly to and from AI models.
    - Handle any mid-operation self-improvement or retraining systems."""

from ultralytics import YOLO
import os


class ModelManager:
    def __init__(self):
        self.object_detection_model = None
        self.model_loaded = False

    def get_latest_model(self, models_dir="models"):
        """
        Finds most recently modified .pt model in dir
        """

        if not os.path.exists(models_dir):
            print(f"Model directory '{models_dir}' not found.")
            return None
        
        pt_files = [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.endswith("pt")]

        if not pt_files:
            print("No model files found. Please download models using the 'functions.ipynb' notebook - function 1.")

        # Sort by modified - THIS MIGHT NOT WORK, modification may occur all at once on download, test this brah
        pt_files.sort(key=os.path.getmtime, reverse=True)
        return pt_files[0]

    def load_object_detection_model(self, model_path=None):
        """
        Loads a YOLO model from a local path.
        """

        if not model_path:
            model_path = self.get_latest_model()

        if not model_path or not os.path.exists(model_path):
            print(f"Model not found at: {model_path}")
            return False
        
        try:
            self.object_detection_model = YOLO(model_path)
            self.model_loaded = True
            print(f"Model loaded: {model_path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def detect_objects(self, image):
        """
        Runs object detection on an image
        """
        if not self.model_loaded:
            raise Exception("Model not loaded. Call load_object_detection_model() first.")
        return self.object_detection_model(image)[0]

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
    
    def run_tracking(self, image):
        """
        Runs tracking on an image
        """
        if not self.model_loaded:
            raise Exception("Model not loaded. Call load_object_detection_model() first.")
        return self.object_detection_model.track(image, persist=True)[0]
    
    def track_objects(self, image):
        """
        Returns bounding box positions of objects and IDs
        """
        
        results = self.run_tracking(image)
        tracks_with_masks = []

        if results.boxes is None or len(results.boxes) == 0:
            return tracks_with_masks
        
        for i in range(len(results.boxes)):
            box = results.boxes[i]

            track_id_tensor = box.id
            track_id = track_id_tensor.int().tolist()[0] if track_id_tensor is not None else None
            class_id = int(box.cls)
            class_name = results.names[class_id]
            confidence = float(box.conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            centre_x, centre_y, w, h = box.xywh[0].tolist()
            
            # Mask handling logic
            mask_polygon_norm = None

            if results.masks is not None and i < len(results.masks):
                mask_polygon_norm = results.masks.xyn[i]
    
            tracks_with_masks.append({
                'class': class_name,
                'track_id': track_id,
                'confidence': confidence,
                'bbox': [x1, y1, x2, y2],
                'centre': [centre_x, centre_y],
                'mask_polygon_norm': mask_polygon_norm
            })

        return tracks_with_masks
        
model_manager = ModelManager()


def load_object_detection_model(model_path=None):
    return model_manager.load_object_detection_model(model_path)

def get_objects(image):
    return model_manager.get_objects(image)

def get_tracking(image):
    return model_manager.track_objects(image)

def load_bound_detector():
    return NotImplementedError

def get_bounds():
    return NotImplementedError

def self_improve():
    return NotImplementedError

