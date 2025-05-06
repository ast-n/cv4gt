""" VIDEO PROCESSING """
""" 
This script should:
    - Take in video streams or files...
    - Manage the frame-by-frame processing loop.
    - Send frames to the AI handler for object detection - FURTHER MODULATE LATER !@!!!!
    - Process prediction results (annotate frames, identify hazards).
    - Send frames with detected hazards to the store module for tagging and saving. 
    - Handles video output generation and display - again, modulate later!!!!
"""

from collections import defaultdict
import ai_handler
import store
import cv2
import numpy as np
from PIL import Image
import os
from obstacle_relevance import get_obstacle_relevance_rating, RELEVANCE_RATING

RELEVANCE_COLORS = {
    5: (0, 0, 255),    # Red - Highest relevance
    4: (0, 165, 255),  # Orange
    3: (0, 255, 255),  # Yellow
    2: (0, 255, 0),    # Green
    1: (255, 255, 0)   # Cyan - Lowest relevance
}

DEFAULT_COLOUR = (255, 0, 0) # Blue
CLASS_IGNORE_LIST = ["sideloader_arm"]


class VideoProcessor:
    def __init__(self):
        """

        Initialises VideoProcessor and loads object detection model

        """
        self.model_ready = False

        # Loading model
        if ai_handler.load_object_detection_model():
            self.model_ready = True
            print("Model sucessfully loaded, now to process")
        else:
            print("Model load failed")
            exit

    def annotate_frame(self, frame, detections, smoothing):
        """

        Helper function to draw bounding boxes and labels on a frame

        """
        
        annotated_frame = frame.copy()
        relevant_objects_found = []

        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            label = f"{det['class']} {det['confidence']:.2f}"

            object_class = det['class']
            confidence = det['confidence']
            
            track_id = det['track_id'].int().tolist()[0]

            relevance = 0
            colour = DEFAULT_COLOUR
            thickness = 1

            if object_class in RELEVANCE_RATING:
                relevance = get_obstacle_relevance_rating(object_class)
                colour = RELEVANCE_COLORS.get(relevance, DEFAULT_COLOUR)
                thickness = 2 if relevance >= 4 else 1

                # Add detection to the lsit if defined relevance
                det['relevance'] =  relevance # Adds to dict
                relevant_objects_found.append(det)

            # Draw label
            label = f"[{track_id}] {object_class} {confidence:.2f} R:{relevance}"    
            
            # Run smoothing
            track = self.track_history[track_id]['history']
            smoothing_offset = self.get_smoothed_box_pos(track)
                        
            x1 += int(smoothing_offset[0])
            y1 += int(smoothing_offset[1])
            x2 += int(smoothing_offset[0])
            y2 += int(smoothing_offset[1])
            
            # Draw rectangle
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), colour, thickness)

            # Draw label background
            text_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, thickness)
            cv2.rectangle(annotated_frame, (x1, text_y - h - 5) , (x1 + w, text_y + 5), colour, -1)
            cv2.putText(annotated_frame, label, (x1, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), thickness)
            
            # Draw tracking line
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated_frame, [points], isClosed=False, color=(230,230,230), thickness=5)
            

        return annotated_frame, relevant_objects_found
    
    
    def get_smoothed_box_pos(self, tracking_history):
        """
        Gets the offset to the new position for the bounding box after object tracking movement smoothing.
        """
        # Can't smooth if there isn't enough history
        if len(tracking_history) < 6:
            return (0,0)
        
        # Separate out the true final position
        final_pos = tracking_history[-1]
        
        prediction_data = np.array(tracking_history)[-6:]
        x_values, y_values = zip(*prediction_data)
        
        coefficients = np.polyfit(x_values, y_values, 1)
        polynomial = np.poly1d(coefficients)
        
        # Get average x distance between points
        differences = [-(x_values[i+1] - x_values[i]) for i in range(len(x_values) - 1)]
        avg_distance = sum(differences) / len(differences) # Could also consider using median here.
        
        x_pred = list(x_values[:-1])
        x_pred.append(x_pred[-1] + avg_distance)
        final_x = x_pred[-1]
        
        final_y = polynomial(x_pred)[-1]
                
        offset = np.subtract((final_x, final_y),(final_pos))
        return np.round(offset)
    
    
    def update_track_ids(self, detections, frame_num):
        """
        Updates tracking history with new frame and cuts any old IDs from the dictionary.
        """
        
        # Update tracking data
        for det in detections:
            track_id = det['track_id'].int().tolist()[0]
            centre_x, centre_y = map(float, det['centre'])
            object_class = det['class']
            
            
            
            self.track_history[track_id]['last_frame'] = frame_num
            track = self.track_history[track_id]['history']
            
            track.append((centre_x, centre_y))
            
            if object_class in CLASS_IGNORE_LIST and len(track) > 1:
                track.pop(0)
            elif len(track) > 20:
                track.pop(0)
                
    
        # Cut old IDs
        cut_list = []
        for tracking_id in self.track_history.keys():
            if self.track_history[tracking_id]['last_frame'] + 40 < frame_num:
                cut_list.append(tracking_id)
                
        for cut_id in cut_list:
            self.track_history.pop(cut_id)
    
    

    def process_video(self, input_video_path, output_video_path=None, display=True, logging=True, smoothing=True):
        """

        Reads video, processes frames, saves and displays

        """

        if not self.model_ready:
            print("Model not loaded. Cannot process frame")

        # Begin video processing
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file: {input_video_path}")
            return
        
        # Get video properties
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Setup for saving if outputing video
        out = None
        if output_video_path:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_video_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            try:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v') if output_video_path.endswith('.mp4') else cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
                print(f"Output video will be saved to: {output_video_path}")
            except Exception as e:
                print(f"Could not create video writer for '{output_video_path}': {e}")
                print("Output video will not be saved.")
                out = None

        # Main video processing loop
        self.track_history = defaultdict(lambda: defaultdict(lambda: []))
        # id: int
        #     last_frame: int
        #     history: []

        
        frame_num = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Finished processing video, or encountered error")
                break

            frame_num += 1
            # Print progress every 100
            if frame_num % 100 == 0:
                print(f"Processing frame {frame_num}")

            # Detect
            """
            try:
                detections = ai_handler.get_objects(frame)
            except Exception as e:
                print(f"Error during detection, on frame: {e}")
                detections = []
            """
                
            # Track
            try:
                tracks = ai_handler.get_tracking(frame)
            except Exception as e:
                print(f"Error during tracking, on frame: {e}")
                tracks = []
                
            # Update track history
            self.update_track_ids(tracks, frame_num)
            
            # Annotate -> hazard identify, to be implemented
            annotated_frame, relevant_objects = self.annotate_frame(frame, tracks, smoothing)

            # Store frame if highly relevant hazard found
            if relevant_objects:
                # Threshold set to 4 for now
                high_relevance_objects = [obj for obj in relevant_objects if obj['relevance'] >= 4]
                # only store at or higher than 4
                if high_relevance_objects:
                    print(f"High relevance object(s) (R>=4) detected in frame {frame_num}: "
                          f"{[(obj['class'], obj['relevance']) for obj in high_relevance_objects]}")
                    if(logging):
                        try:
                            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                            stored_path = store.tag_and_store(img_pil)
                            print(f"Stored frame with high relevance objects at: {stored_path}")
                        except Exception as e:
                            print(f"Warning: Failed to store frame {frame_num}: {e}")
            
            # Write frames as output
            if out:
                out.write(annotated_frame)

            # Display frames
            if display:
                cv2.imshow("Hazard detection", annotated_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    print("Quitting")
                    break

        cap.release()
        if out:
            out.release()
        if display:
            cv2.destroyAllWindows()