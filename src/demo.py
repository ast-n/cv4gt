"""

cv4gt - 1st PoC demonstration script

"""
from video_processing import VideoProcessor
import os

def main():
    # Config
    INPUT_VIDEO = "data/input.mp4"
    OUTPUT_VIDEO = "data/output.avi"
    ENABLE_DISPLAY = True
    ENABLE_LOGGING = False

    if not os.path.isfile(INPUT_VIDEO):
        print(f"Input video file not found: {INPUT_VIDEO}")
        print("Please make sure the file exists.")
        return 
    
    # Run
    try:
        processor = VideoProcessor()

        processor.process_video(
            input_video_path=INPUT_VIDEO,
            output_video_path=OUTPUT_VIDEO,
            display=ENABLE_DISPLAY,
            logging=ENABLE_LOGGING
        )

    except Exception as e:
        print("Error, see traceback")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()