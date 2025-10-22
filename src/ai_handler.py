"""AI Handler Module.

This module manages model loading, object detection, and tracking functionality with ByteTrack.
It provides the ModelManager class that handles YOLO model operations + ByteTrack
object tracking, with functions for common operations.

The module integrates YOLO object detection with ByteTrack for persistent object
tracking across video frames, running inference asynchronously to avoid blocking.
"""

from ultralytics import YOLO
import os
import asyncio
from utils.bytetracker.tracker.byte_tracker import BYTETracker, STrack
import numpy as np

class TrackerArgs:
    """Configuration arguments for ByteTracker.

    This class holds the configuration parameters for the ByteTrack object tracker.
    These arguments control tracking behavior including detection thresholds, track
    buffering, and matching sensitivity.

    Attributes:
        track_thresh (float): Minimum confidence threshold for tracking (0.25).
        track_buffer (int): Number of frames to buffer lost tracks (30).
        match_thresh (float): IoU threshold for track matching (0.8).
        mot20 (bool): Whether to use MOT20 protocol (False).
    """
    def __init__(self):
        self.track_thresh = 0.25
        self.track_buffer = 30
        self.match_thresh = 0.8
        self.mot20 = False

class ModelManager:
    """Manages models for object detection and tracking.

    This class handles loading of YOLO models, running object detection inference,
    and maintaining a ByteTrack tracker instance for persistent object IDs across frames.
    All inference operations are designed to run asynchronously via thread pool
    executors to avoid blocking the async event loop.

    Attributes:
        object_detection_model (YOLO): The loaded YOLO model instance.
        model_loaded (bool): Flag indicating whether a model is loaded.
        tracker (BYTETracker): ByteTrack tracker instance for object tracking.
    """
    def __init__(self):
        self.object_detection_model = None
        self.model_loaded = False
        # Tracker instance
        tracker_args = TrackerArgs()
        self.tracker = BYTETracker(args=tracker_args, frame_rate=30)

    def get_latest_model(self, models_dir="models"):
        """Find the most recently modified YOLO model file.

        Searches the specified directory for .pt model files and returns the
        path to the most recently modified one.

        Args:
            models_dir (str, optional): Directory to search for models. Defaults to "models".

        Returns:
            str or None: Path to the latest model file, or None if directory doesn't exist
                or no models are found.
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
        """Load a YOLO object detection model.

        Loads a YOLO model from the specified path or automatically finds the
        latest model if no path is provided.

        Args:
            model_path (str, optional): Path to the YOLO model file (.pt). If None,
                automatically loads the latest model from the models directory.

        Returns:
            bool: True if model loaded successfully, False otherwise.
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
        """Run YOLO object detection on an image.

        Args:
            image (numpy.ndarray): Input image as a NumPy array.

        Returns:
            ultralytics.engine.results.Results: YOLO detection results containing
                boxes, confidences, and class predictions.

        Raises:
            Exception: If no model is loaded.
        """
        if not self.model_loaded:
            raise Exception("Model not loaded. Call load_object_detection_model() first.")
        return self.object_detection_model(image)[0]

    def get_objects(self, image):
        """Get detected objects with bounding boxes and metadata.

        Runs object detection and formats the results into a list of dictionaries
        containing class information, confidence scores, and bounding boxes.

        Args:
            image (numpy.ndarray): Input image as a NumPy array.

        Returns:
            list[dict]: List of detected objects, where each dict contains:
                - 'class' (str): Object class name
                - 'class_id' (int): Numeric class ID
                - 'confidence' (float): Detection confidence score
                - 'bbox' (list[float]): Bounding box as [x1, y1, x2, y2]
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
        """Proxy method for running ByteTrack update in a thread pool.

        This synchronous method wraps the tracker's update call, allowing it to
        be executed in a background thread via asyncio's run_in_executor.

        Args:
            detections_for_tracker (numpy.ndarray): Array of detections with shape
                (N, 6) containing [x1, y1, x2, y2, score, class_id].
            image_info (tuple): Image dimensions as (height, width).

        Returns:
            list[STrack]: List of active tracks with updated positions and IDs.
        """
        # Tracker's update method is synchronous and CPU bound
        return self.tracker.update(detections_for_tracker, image_info, image_info)
    
    def proxy_predict(self, image, verbose):
        """Proxy method for running YOLO prediction in a thread pool.

        This synchronous method wraps the model's predict call, allowing it to
        be executed in a background thread via asyncio's run_in_executor.

        Args:
            image (numpy.ndarray): Input image as a NumPy array.
            verbose (bool): Whether to print prediction information.

        Returns:
            list[ultralytics.engine.results.Results]: List containing YOLO results.
        """
        return self.object_detection_model.predict(image, verbose=verbose)
    
    async def track_objects(self, image):
        """Track objects across frames using YOLO detection and ByteTrack.

        Combines YOLO object detection with ByteTrack tracking to maintain
        persistent object IDs across video frames. Runs inference and tracking
        in background threads to avoid blocking the async event loop.

        Args:
            image (numpy.ndarray): Input image as a NumPy array.

        Returns:
            list[dict]: List of tracked objects, where each dict contains:
                - 'class' (str): Object class name
                - 'class_id' (int): Numeric class ID
                - 'track_id' (int): Persistent tracking ID
                - 'confidence' (float): Detection confidence score
                - 'bbox' (list[float]): Bounding box as [x1, y1, x2, y2]
                - 'centre' (list[float]): Box center as [cx, cy]
                - 'mask_polygon_norm' (None): Placeholder for future mask support
        """
        # Get raw detections from YOLOv8
        #results = self.object_detection_model.predict(image)[0]

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(None, self.proxy_predict, image, False)
        results = results[0]
    
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

        # Run synchronous tracker update in background thread
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
    """Convenience function to load object detection model.

    Args:
        model_path (str, optional): Path to the YOLO model file.

    Returns:
        bool: True if model loaded successfully, False otherwise.
    """
    return model_manager.load_object_detection_model(model_path)

def get_objects(image):
    """Convenience function to get detected objects.

    Args:
        image (numpy.ndarray): Input image.

    Returns:
        list[dict]: List of detected objects with metadata.
    """
    return model_manager.get_objects(image)

async def get_tracking(image):
    """Convenience function to get tracked objects asynchronously.

    Args:
        image (numpy.ndarray): Input image.

    Returns:
        list[dict]: List of tracked objects with persistent IDs.
    """
    return await model_manager.track_objects(image)


