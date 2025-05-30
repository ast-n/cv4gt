"""
cv4gt - Proof-of-concept demonstration script
"""
from video_processing import VideoProcessor
import os

def main():
    # Config
    INPUT_VIDEO = "data\\recordings\\HD720_SN33773243_10-13-17.svo2"
    USING_ZED = True
    OUTPUT_VIDEO = "data/output.avi"
    ENABLE_DISPLAY = True
    ENABLE_LOGGING = False
    COLOUR_CORRECTION = False
    SMOOTHING_FACTOR = 0.0
    MODEL_PATH = "models\\YOLOv8-cv4gt-data-15-04_100e.pt"

    if not os.path.isfile(INPUT_VIDEO):
        print(f"Input video file not found: {INPUT_VIDEO}")
        print("Please make sure the file exists.")
        return 
    
    # Run
    try:
        processor = VideoProcessor(MODEL_PATH)

        processor.process_video(
            input_video_path=INPUT_VIDEO,
            using_zed=USING_ZED,
            output_video_path=OUTPUT_VIDEO,
            display=ENABLE_DISPLAY,
            logging=ENABLE_LOGGING,
            smoothing=SMOOTHING_FACTOR,
            enable_colour_correction=COLOUR_CORRECTION
        )

    except Exception as e:
        print("Error, see traceback")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()