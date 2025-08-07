from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from video_processing import VideoProcessor
import cv2

# Config
INPUT_VIDEO = "data\\ground_truth.mp4"
USING_ZED = False
OUTPUT_VIDEO = "data/output.avi"
ENABLE_DISPLAY = False
ENABLE_LOGGING = False
COLOUR_CORRECTION = False
SMOOTHING_FACTOR = 0.0
MODEL_PATH = "models\\YOLOv8s-cv4gt-data-20-05_239e.onnx"
ZED_OBJECT_DETECT = False

processor = VideoProcessor(MODEL_PATH, ZED_OBJECT_DETECT)

app = FastAPI()

def video_generator(VP: VideoProcessor):
    for frame in VP.process_video(
            input_video_path=INPUT_VIDEO,
            using_zed=USING_ZED,
            output_video_path=OUTPUT_VIDEO,
            display=ENABLE_DISPLAY,
            logging=ENABLE_LOGGING,
            smoothing=SMOOTHING_FACTOR,
            enable_colour_correction=COLOUR_CORRECTION
        ):
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/view/annotated_video")
def get_annotated_video():
    return StreamingResponse(video_generator(processor), media_type="multipart/x-mixed-replace; boundary=frame")
