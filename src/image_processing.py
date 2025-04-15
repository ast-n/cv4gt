from __future__ import annotations

""" IMAGE PROCESSING """
""" This script:
    - Takes in key frames. 
    - Runs data pre-processing for the AI.
    - Sends images to the object-recognition module.
    - Processes prediction results from the object-recognition module.
    - Sends frames off to be GPS tagged.
    - Finds bounds of detected hazards and rates their relevance.
"""

import ai_handler
import store
import cv2
import numpy as np
from PIL import Image
from obstacle_relevance import get_obstacle_relevance_rating 
from obstacle_relevance import RELEVANCE_RATING

class ImageProcessor:
    def __init__(self):
        self.input_queue = []
        ai_handler.load_object_detection_model()

    def add_frame(self, frame):
        """
        Add frame to the processing queue
        """
        self.input_queue.append(frame)

    def send_to_object_detection(self, image):
        """Send image to the AI model for object detection"""
        return ai_handler.get_objects(image)

    def process_next_frame(self):
        """
        Process the next frame in queue
        """
        if not self.input_queue:
            return None
        
        frame = self.input_queue.pop(0)

        detections = self.send_to_object_detection(frame)

        stored_path = None
        if detections:
            hazards = []  # Initialize hazards list

            # Process each detection
            for d in detections:
                if d['class'] in RELEVANCE_RATING:
                    d['relevance'] = get_obstacle_relevance_rating(d['class'])  # Add relevance score
                    hazards.append(d)

            if hazards:
                image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                stored_path = store.tag_and_store(image_pil)

                # Add bounding boxes and display the relevance score
                for hazard in hazards:
                    x1, y1, x2, y2 = [int(coord) for coord in hazard['bbox']]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{hazard['class']} {hazard['confidence']:.2f} R:{hazard['relevance']}", 
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return {
            'frame': frame,
            'detections': detections,
            'stored_path': stored_path if 'stored_path' in locals() else None
        }

    def preprocess_image(self, image):
        """
        Preprocess the image for object detection (stub)
        """
        raise NotImplementedError("Preprocessing not yet implemented")

    def process_all_frames(self):
        """
        Process all frames in queue
        """
        results = []
        while self.input_queue:
            result = self.process_next_frame()
            if result:
                results.append(result)
        return results

# Instance of ImageProcessor
image_processor = ImageProcessor()          

# Helper Functions
def send_to_object_detection(image):
    return image_processor.send_to_object_detection(image)

def send_to_tag(image):
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    return store.tag_and_store(image_pil)

def get_bounds(detections):
    bounds = []
    for detection in detections:
        bounds.append(detection['bbox'])
    return bounds