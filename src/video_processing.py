from collections import defaultdict
import ai_handler
import store
import cv2
import numpy as np
from PIL import Image
import os
import onnx
import ast

from obstacle_relevance import get_obstacle_relevance_rating, get_object_median_depths, MAX_DEPTH, RELEVANCE_RATING
import colour_correction
import camera_feed
import store
from enum import Enum

RELEVANCE_COLORS = {
    5: (0, 0, 255),    # Red - Highest relevance
    4: (0, 165, 255),  # Orange
    3: (0, 255, 255),  # Yellow
    2: (0, 255, 0),    # Green
    1: (255, 255, 0)   # Cyan - Lowest relevance
}

class GripperState(Enum):
    NEUTRAL = 0
    GOOD = 1
    BAD = 2
    NONE = 3

DEFAULT_COLOUR = (255, 0, 0) # Blue
DEFAULT_TEXT_COLOUR = (255, 255, 255) # White
CLASS_IGNORE_LIST = ["sideloader_arm"]

class VideoProcessor:
    def __init__(self, model_path=None, zed_object_detect=False):
        """
        Initialises VideoProcessor and loads object detection model
        """
        self.model_ready = False
        self.model_path = model_path

        if ai_handler.load_object_detection_model(model_path):
            self.model_ready = True
            print("Model successfully loaded, now to process")
        else:
            print("Model load failed")
            exit()

    def annotate_frame(self, frame, detections, smoothing):
        """
        Helper function to draw bounding boxes and labels on a frame.
        """
        
        annotated_frame = frame.copy()
        H, W, _ = frame.shape # Mask scaling
        relevant_objects_found = []
        gripper_state = GripperState.NONE
        
        indicator_x_line1 = int(W * 0.45)
        indicator_x_line2 = int(W * 0.65)
        indicator_y1 = int(H * 0.1)
        indicator_y2 = int(H * 0.9)

        for det in detections:
            if det['track_id'] is None:
                continue
                
            x1, y1, x2, y2 = map(int, det['bbox'])
            object_class = det['class']
            confidence = det['confidence']
            track_id = det['track_id'] # Already an int
            depth = det['depth']
            
            velocity = 0
            if 'velocity' in det.keys():
                if not np.any(np.isnan(det['velocity'])):
                    velocity = np.linalg.norm(det['velocity']) # Linear norm a.k.a. magnitude

            # --- Filter out objects that are too far ---
            if depth > MAX_DEPTH:
                continue  # Skip object
            
            relevance = 0
            colour = DEFAULT_COLOUR
            text_colour = DEFAULT_TEXT_COLOUR
            thickness = 1

            if object_class in RELEVANCE_RATING:
                relevance = get_obstacle_relevance_rating(object_class, depth, velocity)
                colour = RELEVANCE_COLORS.get(relevance, DEFAULT_COLOUR)
                thickness = 2 if relevance >= 4 else 1
                text_colour = (0, 0, 0) if sum(colour)/3 > 127 else text_colour

                # Add detection to the list if relevance is defined
                det['relevance'] = relevance  # Adds to dict
                relevant_objects_found.append(det)

            # Run smoothing
            track = self.track_history[track_id]['history']
            if smoothing:
                smoothing_offset = self.get_smoothed_box_pos(track)
                smoothing_offset = np.multiply(smoothing_offset, smoothing)
                
                x1 += int(smoothing_offset[0])
                y1 += int(smoothing_offset[1])
                x2 += int(smoothing_offset[0])
                y2 += int(smoothing_offset[1])

            # Cut off drawing here if relevance 0
            if relevance == 0:
                continue
            
            if object_class == "bin" and gripper_state != GripperState.BAD: # Bad gripper state overrides all
                if gripper_state == GripperState.NONE:
                    gripper_state = GripperState.NEUTRAL
                    
                bin_inside = [indicator_x_line1 <= x1 <= indicator_x_line2 and indicator_y1 <= y1 <= indicator_y2, indicator_x_line1 <= x2 <= indicator_x_line2 and indicator_y1 <= y2 <= indicator_y2]
                if all(bin_inside):
                    gripper_state = GripperState.GOOD
                elif any(bin_inside):
                    gripper_state = GripperState.BAD

            # Handle mask drawing
            if det.get('mask_polygon_norm') is not None:
                polygon_norm = det.get('mask_polygon_norm')
                polygon_pixel = (polygon_norm * np.array([W, H])).astype(np.int32)

                # Draw polygon
                cv2.polylines(annotated_frame, [polygon_pixel], isClosed=True, color=colour, thickness=2)

                # Draw bounding box - a bit lighter
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), colour, 1)
            else:
                # Draw standard bounding box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), colour, thickness)

            # Draw label with all information - moved this
            label = f"{object_class} {confidence:.2f} R:{relevance} D:{depth:.1f}m"
            
            # Draw label background
            text_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, thickness)
            cv2.rectangle(annotated_frame, (x1, text_y - h - 5), (x1 + w, text_y + 5), colour, -1)
            cv2.putText(annotated_frame, label, (x1, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_colour, thickness)

            # Draw tracking line
            """
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated_frame, [points], isClosed=False, color=(230,230,230), thickness=5)
            """
            
        # Draw bin alignment indicator
        if gripper_state != GripperState.NONE:
            match gripper_state:
                case GripperState.GOOD:
                    gripper_colour = (0,255,0)
                    gripper_icon = store.get_grabber_indicator("check")
                case GripperState.BAD:
                    gripper_colour = (0,0,255)
                    gripper_icon = store.get_grabber_indicator("cross")
                case _:
                    gripper_colour = (255,255,255)
                    gripper_icon = None
            
            cv2.line(annotated_frame, (indicator_x_line1, indicator_y1), (indicator_x_line1, indicator_y2), gripper_colour, thickness=4)
            cv2.line(annotated_frame, (indicator_x_line2, indicator_y1), (indicator_x_line2, indicator_y2), gripper_colour, thickness=4)
            
            if gripper_icon is not None:
                self.overlay_transparent(annotated_frame, gripper_icon, (indicator_x_line1+indicator_x_line2)//2-32, indicator_y1)

        return annotated_frame, relevant_objects_found
    
    # Used for overlaying the bin gripper warning/checkmark icon
    def overlay_transparent(self, background, overlay, x, y):

        background_width = background.shape[1]
        background_height = background.shape[0]

        if x >= background_width or y >= background_height:
            return background

        h, w = overlay.shape[0], overlay.shape[1]

        if x + w > background_width:
            w = background_width - x
            overlay = overlay[:, :w]

        if y + h > background_height:
            h = background_height - y
            overlay = overlay[:h]

        if overlay.shape[2] < 4:
            overlay = np.concatenate(
                [
                    overlay,
                    np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
                ],
                axis = 2,
            )

        overlay_image = overlay[..., :3]
        mask = overlay[..., 3:] / 255.0

        background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    def get_smoothed_box_pos(self, tracking_history):
        """
        Gets the offset to the new position for the bounding box after object tracking movement smoothing.
        """
        # Can't smooth if there isn't enough history
        if len(tracking_history) < 6:
            return (0, 0)
        
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
                
        offset = np.subtract((final_x, final_y), (final_pos))
        return np.round(offset)

    def update_track_ids(self, detections, frame_num):
        """
        Updates tracking history with new frame and cuts any old IDs from the dictionary.
        """
        # Update tracking data
        for det in detections:
            track_id = det['track_id'] # already an int
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

    def process_video(self, input_video_path=None, use_realsense=True, output_video_path=None, display=True, logging=True, smoothing=1.0, enable_colour_correction=True):
        """
        Reads video, processes frames, saves and displays
        """
        if not self.model_ready:
            print("Model not loaded. Cannot process frame")
            return

        if use_realsense:
            print("Using RealSense camera feed.")
            camera_feed.setup_cam(recording_path=input_video_path)
            frame_width, frame_height = camera_feed.realsense_cam.get_resolution()
            fps = camera_feed.realsense_cam.get_fps()
        else:
            print("Using standard video file (OpenCV).")
            if not input_video_path:
                raise ValueError("An input video path is required when not using RealSense.")
            cap = cv2.VideoCapture(input_video_path)
            if not cap.isOpened():
                print(f"Error: Could not open video file: {input_video_path}")
                return
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Setup for saving if outputting video
        out = None
        if output_video_path:
            output_dir = os.path.dirname(output_video_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            try:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v') if output_video_path.endswith('.mp4') else cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
                print(f"Output video will be saved to: {output_video_path}")
            except Exception as e:
                print(f"Could not create video writer for '{output_video_path}': {e}")
                out = None

        # Main video processing loop
        self.track_history = defaultdict(lambda: defaultdict(lambda: []))
        
        frame_num = 0
        try:

            while True:
                if use_realsense:
                    aligned_frames, success = camera_feed.get_frames()
                    if not success:
                        break
                    frame = camera_feed.get_image(aligned_frames)
                    depth_map = camera_feed.get_depth_map(aligned_frames)
                else: # Using standard video 
                    ret, frame = cap.read()
                    if not ret:
                        break
                    depth_map = None

                if frame is None:
                    continue

                frame_num += 1
                if frame_num % 100 == 0:
                    print(f"Processing frame {frame_num}")

                # Colour conversion
                if (enable_colour_correction):
                    try:
                        frame = colour_correction.colour_convert(frame)
                    except Exception as e:
                        print(f"Error during colour correction, on frame: {e}")
                
                # Detect and track objects
                try:
                    tracks = ai_handler.get_tracking(frame)
                except Exception as e:
                    print(f"Error during tracking, on frame: {e}")
                    tracks = []
                    
                tracks = get_object_median_depths(tracks, depth_map=depth_map)
                
                # Update track history
                self.update_track_ids(tracks, frame_num)

                # Annotate -> hazard identify, to be implemented
                annotated_frame, relevant_objects = self.annotate_frame(frame, tracks, smoothing)

                # Store frame if highly relevant hazard found
                if relevant_objects:
                    high_relevance_objects = [obj for obj in relevant_objects if obj['relevance'] >= 5]
                    if high_relevance_objects:
                        print(f"High relevance object(s) (R>=4) detected in frame {frame_num}: "
                            f"{[(obj['class'], obj['relevance']) for obj in high_relevance_objects]}")
                        if logging: # ----------------- THIS REALLY NEEDS TO BE ASYNCED SOMEHOW. THIS CODE IS WAY TOO SLOW TO RUN IN THE MAIN LOOP. MAYBE HAVE SOME FUNCTION OUTSIDE HERE READ THE FRAMES AND DO THIS SAVING SEPARATELY?
                                    # The plan is to catch this in the API loop then do multiprocessing.Process on the method to make it run independently.
                            try:
                                img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                                stored_path = store.tag_and_store(img_pil)
                                print(f"Stored frame with high relevance objects at: {stored_path}")
                            except Exception as e:
                                print(f"Warning: Failed to store frame {frame_num}: {e}")

                # Write frames as output
                if out:
                    out.write(annotated_frame)

                # Yield frame
                yield annotated_frame, relevant_objects
                
                # Display frames
                if display:
                    cv2.imshow("Hazard detection", annotated_frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:
                        print("Quitting")
                        break
        finally:
            camera_feed.shutdown_cam()
            if out:
                out.release()
            if display:
                cv2.destroyAllWindows()