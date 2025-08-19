from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
import cv2
import json
import os

from video_processing import VideoProcessor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Config
INPUT_VIDEO = os.path.join(BASE_DIR, "data", "ground_truth.mp4")
# INPUT_VIDEO = None
USE_REALSENSE = False
# USE_REALSENSE = True
OUTPUT_VIDEO = os.path.join(BASE_DIR, "data", "output.avi")
ENABLE_DISPLAY = False
ENABLE_LOGGING = False
COLOUR_CORRECTION = False
SMOOTHING_FACTOR = 0.0


MODEL_PATH = os.path.join(BASE_DIR, "models", "YOLOv8s-10-06-193e.pt")

processor = VideoProcessor(MODEL_PATH)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def get_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        for frame, objects in processor.process_video(
            input_video_path=INPUT_VIDEO,
            use_realsense=USE_REALSENSE,
            output_video_path=OUTPUT_VIDEO,
            display=ENABLE_DISPLAY,
            logging=ENABLE_LOGGING,
            smoothing=SMOOTHING_FACTOR,
            enable_colour_correction=COLOUR_CORRECTION
            ):
            
            ret, buffer = cv2.imencode('.jpg', frame)
            
            await websocket.send_text(json.dumps(objects))
            await websocket.send_bytes(buffer.tobytes())
            
            await asyncio.sleep(0.001)
    except (WebSocketDisconnect, ConnectionClosed):
        print("Client disconnected")

#I think the plan here is to make the streaming response return a JSON or something with the frame and other info attached,
# then the frontend just extracts the relevant elements?

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)