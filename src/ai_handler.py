""" AI HANDLER
This script should:
    - Handle setup and loading of AI models into memory.
    - Handle passing data directly to and from AI models.
    - Handle any mid-operation self-improvement or retraining systems."""

from ultralytics import YOLO
import os
import asyncio
from utils.bytetracker.tracker.byte_tracker import BYTETracker, STrack
import numpy as np

class TrackerArgs:
    """
    Class to hold tracker config args, since these are not accurate in ByteTracker implementation
    """
    def __init__(self):
        self.track_thresh = 0.25
        self.track_buffer = 30
        self.match_thresh = 0.8
        self.mot20 = False

class ModelManager:
    def __init__(self):
        self.object_detection_model = None
        self.model_loaded = False
        # Tracker instance
        tracker_args = TrackerArgs()
        self.tracker = BYTETracker(args=tracker_args, frame_rate=30)

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
                'class_id': class_id,
                'confidence': confidence,
                'bbox': [x1, y1, x2, y2]
            })
        return detections
    
    def proxy_bytetrack_update(self, detections_for_tracker, image_info):
        # Tracker's update method is synchronous and CPU
        return self.tracker.update(detections_for_tracker, image_info, image_info)
    
    async def track_objects(self, image):
        """
        Returns bounding box positions of objects and IDs using decoupled ByteTrack tracker.
        """        
        # Get raw detections from YOLOv8
        #results = self.object_detection_model.predict(image)[0]

        results = self.object_detection_model.predict(image, verbose=False)[0]
    
        # Format detections for ByteTrack
        detections_list = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            score = float(box.conf)
            class_id = int(box.cls)
            detections_list.append([x1, y1, x2, y2, score, class_id])

        if not detections_list:
            return []

        detections_for_tracker = np.array(detections_list)

        # Get image dimensions to pass 
        img_h, img_w = image.shape[:2]

        # Run synchrnous tracker update in background thread
        loop = asyncio.get_running_loop()
        online_tracks = await loop.run_in_executor(None, self.proxy_bytetrack_update, detections_for_tracker, (img_h, img_w))
        
        # Format tracker output into desired structure
        tracks_with_masks = []
        for track in online_tracks:
            x1, y1, x2, y2 = track.tlbr
            track_id = track.track_id
            class_id = int(track.class_id)
            class_name = results.names[class_id]

            tracks_with_masks.append({
                'class': class_name,
                'class_id': class_id,
                'track_id': track_id,
                'confidence': track.score,
                'bbox': [x1, y1, x2, y2],
                'centre': [(x1 + x2) / 2, (y1 + y2) / 2],
                'mask_polygon_norm': None
            })

        return tracks_with_masks
    
model_manager = ModelManager()

def load_object_detection_model(model_path=None):
    return model_manager.load_object_detection_model(model_path)

def get_objects(image):
    return model_manager.get_objects(image)

async def get_tracking(image):
    return await model_manager.track_objects(image)

def load_bound_detector():
    return NotImplementedError

def get_bounds():
    return NotImplementedError

def self_improve():
    return NotImplementedError

