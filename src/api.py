from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
import cv2
import json
import time

from video_processing import VideoProcessor

# Config
INPUT_VIDEO = "data/input.mp4"
USE_REALSENSE = False
#OUTPUT_VIDEO = "data/output.avi"
OUTPUT_VIDEO = None
ENABLE_DISPLAY = False
ENABLE_LOGGING = False
COLOUR_CORRECTION = False
SMOOTHING_FACTOR = 0.0
FPS_CAP = 30 # Set to 0 to turn off.

MODEL_PATH = "models/YOLOv8s-10-06-193e.pt"

processor = VideoProcessor(MODEL_PATH)

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def get_stream(websocket: WebSocket):
    if FPS_CAP == 0:
        frametime = 0
    else:
        frametime = 1/FPS_CAP
        
    await websocket.accept()
    
    try:
        async for frame, objects in processor.process_video(
            input_video_path=INPUT_VIDEO,
            use_realsense=USE_REALSENSE,
            output_video_path=OUTPUT_VIDEO,
            display=ENABLE_DISPLAY,
            logging=ENABLE_LOGGING,
            smoothing=SMOOTHING_FACTOR,
            ):
            starttime = time.monotonic()
            
            ret, buffer = cv2.imencode('.jpg', frame)
            
            await websocket.send_text(json.dumps(objects))
            await websocket.send_bytes(buffer.tobytes())
            
            elapsedtime = time.monotonic() - starttime
            if elapsedtime < frametime:
                await asyncio.sleep(frametime - elapsedtime) # Return control to main loop with asyncio while pausing to ensure framerate.
            else:
                await asyncio.sleep(0)
    except (WebSocketDisconnect, ConnectionClosed):
        print("Client disconnected")

#I think the plan here is to make the streaming response return a JSON or something with the frame and other info attached,
# then the frontend just extracts the relevant elements?

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)