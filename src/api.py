from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
import cv2
import json
import time
import sys, os
import psutil

from video_processing import VideoProcessor, begin_task
import store

# Config
INPUT_VIDEO = "data/ground_truth.mp4"
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

    last_sys_update = 0  
    
    try:
        async for frame, objects in processor.process_video(
            input_video_path=INPUT_VIDEO,
            use_realsense=USE_REALSENSE,
            output_video_path=OUTPUT_VIDEO,
            display=ENABLE_DISPLAY,
            logging=ENABLE_LOGGING,
            smoothing=SMOOTHING_FACTOR,
            ):
            # Begin grabbing GPS early so it can run while websocket data is sending since it seems kinda slow
            gps_loc = await begin_task(store.get_gps())
            
            starttime = time.monotonic()
            
            ret, buffer = cv2.imencode('.jpg', frame)
            
            wrapped_objects = {"event": "objects", "content": objects}
            await websocket.send_text(json.dumps(wrapped_objects))
            await websocket.send_bytes(buffer.tobytes())
            
            wrapped_gps = {"event": "location", "content": await gps_loc}
            await websocket.send_text(json.dumps(wrapped_gps))

            
            now = time.monotonic()
            if now - last_sys_update >= 1:
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory()
                wrapped_sys = {
                    "event": "system",
                    "content": {
                        "cpu": cpu,
                        "usedMB": round(mem.used / (1024 * 1024)),
                        "totalMB": round(mem.total / (1024 * 1024)),
                    },
                }
                await websocket.send_text(json.dumps(wrapped_sys))
                last_sys_update = now
            
            elapsedtime = time.monotonic() - starttime
            if elapsedtime < frametime:
                await asyncio.sleep(frametime - elapsedtime) # Return control to main loop with asyncio while pausing to ensure framerate.
            else:
                await asyncio.sleep(0)
    except (WebSocketDisconnect):
        print("Client disconnected")
    except (ConnectionClosed):
        print("Connection closed")
    finally:
        if ENABLE_LOGGING:
            store.save_and_close_log() 


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)