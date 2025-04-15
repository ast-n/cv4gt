"""

cv4gt - 1st PoC demonstration script

"""

import cv2
import os
from image_processing import image_processor
from ai_handler import load_object_detection_model


def process_video(video_path, output_path=None, model_path="models/YOLOv8-cv4gt-data-11-04_10e.pt"):
    """
    Process a video file and detect hazards
    """

    # Load the model
    if not load_object_detection_model(model_path):
        print("Failed to load model. Exiting")
        return
    
    # Open video
    print(f"Trying to open video: {video_path}")
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    # Get video data
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture.get(cv2.CAP_PROP_FPS)

    # Create output video writer if output path is provided
    out = None
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    
    # Process the video frame by frame
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break
            
        frame_count += 1
        print(f"Processing frame {frame_count}")
        
        # Add frame to processor
        image_processor.add_frame(frame)
        
        # Process the frame
        result = image_processor.process_next_frame()
        
        if result:
            # Display detection info
            for i, detection in enumerate(result['detections']):
                print(f"  Detection {i+1}: {detection['class']} ({detection['confidence']:.2f})")
            
            # Write frame to output if needed
            if out:
                print("Writing frame to video")
                out.write(result['frame'])
                
            # Display the frame
            cv2.imshow('CV4GT Detection', result['frame'])
            
            # Break on ESC key
            if cv2.waitKey(1) & 0xFF == 27:
                break
    
    # Release resources
    capture.release()
    if out:
        out.release()
    cv2.destroyAllWindows()
    
    print(f"Processed {frame_count} frames")


if __name__ == "__main__":
    # Make sure to replace this with the actual video file path
    process_video("data/input.mp4", output_path="data/output_clip.avi", model_path="models/YOLOv8-cv4gt-bad-dataset_epochs500.pt")