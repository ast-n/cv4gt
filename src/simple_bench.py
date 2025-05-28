import cv2
import argparse
import os
import numpy as np
import time
from ultralytics import YOLO

# Try importing ZED - make it optional to allow testing without ZED SDK
try:
    import pyzed.sl as sl
    ZED_AVAILABLE = True
    print("PyZED SDK found.")
except ImportError:
    print("WARNING: PyZED SDK not found. 'camera' source will not be available.")
    ZED_AVAILABLE = False

def setup_zed_camera():
    """Initializes and opens the ZED camera."""
    if not ZED_AVAILABLE:
        print("Error: ZED SDK is not available.")
        return None, None

    print("Initializing ZED camera...")
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720  # Start with HD720, can change
    init_params.camera_fps = 30
    init_params.sdk_verbose = 0  # Keep logs clean unless debugging

    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Error opening ZED camera: {err}")
        print("Ensure the camera is connected and not in use by another process.")
        return None, None

    runtime_params = sl.RuntimeParameters()
    image_mat = sl.Mat()  # ZED image object
    print("ZED camera opened successfully.")
    return zed, runtime_params, image_mat

def setup_video_capture(filepath):
    """Initializes and opens a video file."""
    print(f"Opening video file: {filepath}")
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        print(f"Error opening video file: {filepath}")
        return None
    print("Video file opened successfully.")
    return cap

def load_yolo_model(model_path):
    """Loads the YOLOv8 TensorRT engine."""
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return None

    print(f"Loading YOLOv8 TensorRT model: {model_path}...")
    try:
        model = YOLO(model_path, task='detect') # Explicitly set task
        print("Model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def main():
    """Main function to run YOLOv8 detection."""
    parser = argparse.ArgumentParser(description="Simple YOLOv8 Real-time Detection (ZED or Video).")
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Input source: 'camera' for ZED, or /path/to/video.mp4"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/YOLOv8s-cv4gt-data-20-05_239e.engine",
        help="Path to the YOLOv8 TensorRT engine file."
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.3, # Slightly higher default
        help="Confidence threshold for detection."
    )
    args = parser.parse_args()
    
    # --- 1. Initialize Input Source FIRST ---
    cap = None
    zed = None
    runtime_params = None
    image_mat = None
    use_zed = False

    if args.source.lower() == 'camera':
        zed, runtime_params, image_mat = setup_zed_camera()
        if zed is None:
            print("Exiting due to ZED camera initialization failure.")
            exit(1)
        use_zed = True
    elif os.path.isfile(args.source):
        cap = setup_video_capture(args.source)
        if cap is None:
            print("Exiting due to video file opening failure.")
            exit(1)
    else:
        print(f"Error: Invalid source '{args.source}'. Must be 'camera' or a valid file path.")
        exit(1)

    # --- 2. Load Model ---
    model = load_yolo_model(args.model)
    if model is None:
        if zed: zed.close() # Clean up ZED if model fails
        if cap: cap.release() # Clean up video if model fails
        print("Exiting due to model loading failure.")
        exit(1)

    # --- 3. Processing Loop ---
    print("\n--- Starting detection loop. Press 'q' to quit. ---")
    window_name = "YOLOv8 Detections"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE) # Create window once

    frame_count = 0
    start_time = time.time()

    while True:
        current_frame_for_cv = None # Frame to be processed by YOLO
        display_frame = None      # Frame to be displayed (can be same as current_frame_for_cv or annotated)
        ret = True

        # --- Get Frame ---
        if use_zed: # Assuming 'use_zed' is set correctly based on args.source
            if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
                zed.retrieve_image(image_mat, sl.VIEW.LEFT)
                frame_bgr_a = image_mat.get_data()

                if frame_bgr_a is not None and isinstance(frame_bgr_a, np.ndarray):
                    # Ensure it's a copy and BGR
                    copied_frame = frame_bgr_a.copy()
                    if copied_frame.shape[2] == 4:
                        current_frame_for_cv = cv2.cvtColor(copied_frame, cv2.COLOR_BGRA2BGR)
                    elif copied_frame.shape[2] == 3:
                        current_frame_for_cv = copied_frame
                    else:
                        print(f"ZED Frame: Unexpected channels {copied_frame.shape[2]}")
                        ret = False
                    display_frame = current_frame_for_cv # Start with the raw frame for display
                else:
                    print("ZED Frame: Failed to get valid data.")
                    ret = False
            else:
                print("ZED: Grab failed.")
                ret = False
        else: # Use cv2.VideoCapture for video files
            ret, current_frame_for_cv = cap.read()
            display_frame = current_frame_for_cv # Start with the raw frame

        if not ret or current_frame_for_cv is None:
            print("End of stream or error reading frame. Exiting loop.")
            break

        frame_count += 1

        # --- Run Inference ---
        try:
            results = model.predict(source=current_frame_for_cv, stream=False, conf=args.conf, verbose=False)
            
            if results and results[0].boxes is not None: # Check if there are actual results
                annotated_frame = results[0].plot() # This should be a NumPy array
                if isinstance(annotated_frame, np.ndarray):
                    display_frame = annotated_frame # Update display_frame with annotations
                else:
                    print("Warning: result.plot() did not return a NumPy array.")
            # If no detections, display_frame remains the original current_frame_for_cv
            
        except Exception as e:
            print(f"An error occurred during prediction or plotting: {e}")
            # display_frame will remain the original current_frame_for_cv
            
        # --- Display the frame ---
        if display_frame is not None:
            cv2.imshow(window_name, display_frame)
        else:
            print("No frame to display.") # Should not happen if ret was True

        # --- Handle GUI and Exit ---
        key = cv2.waitKey(1) & 0xFF # Crucial: process OpenCV GUI events and wait 1ms
        if key == ord('q'):
            print("'q' pressed, exiting.")
            break
        
        # REMOVED: The cv2.getWindowProperty check for now

        # Your FPS calculation can go here if needed, outside the try-except for prediction
        if frame_count % 30 == 0:
             # ... (your FPS calculation logic, make sure it doesn't crash if result.speed is missing) ...
             # For simplicity, you can just print frame_count for now
             print(f"Processed frame: {frame_count}")


    # --- 4. Cleanup ---
    print("Cleaning up resources...")
    if use_zed and zed.is_opened(): # Check if zed was initialized
        zed.close()
    if cap is not None and cap.isOpened(): # Check if cap was initialized
        cap.release()
    cv2.destroyAllWindows()
    print("Done.")

if __name__ == "__main__":
    # Make sure to define or pass 'args', 'zed', 'cap', 'image_mat', 
    # 'runtime_params', 'use_zed', 'model' into main or structure appropriately
    # The provided simple_bench.py likely defines these within main() already.
    # This snippet focuses on the loop structure.
    main()