"""FastAPI Backend Server.

This module implements the HTTP and WebSocket server for the CV4GT system.
It provides a WebSocket endpoint that streams processed video frames and
detection data to connected clients (the Electron frontend).

The server:
- Loads configuration from config.ini
- Initialises the VideoProcessor for AI inference
- Streams JPEG-encoded frames and JSON detection data via WebSocket
- Sends GPS location and system metrics periodically
- Handles graceful shutdown and logging
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import cv2
import json
import time
from configparser import ConfigParser
import psutil
from turbojpeg import TurboJPEG
import platform

from video_processing import VideoProcessor, begin_task
import store

config = ConfigParser(inline_comment_prefixes=';')

def on_jetson():
    if platform.system() == "Linux":
        if platform.machine() == "aarch64":
            uname_info = platform.uname()
            if "tegra" in uname_info.release.lower() or "tegra" in uname_info.version.lower():
                return True
    
    return False

if on_jetson():
    config.read("config_jetson.ini") # Load config for Jetson
else:
    config.read("config.ini") # Load config for non-Jetson


video_config = config['VIDEO']
# Video Config
INPUT_VIDEO = video_config['input_video']
USE_REALSENSE = video_config.getboolean('use_realsense')
OUTPUT_VIDEO = video_config['output_video']
ENABLE_DISPLAY = video_config.getboolean('enable_auxiliary_display')
SMOOTHING_FACTOR = float(video_config['smoothing_factor'])
FPS_CAP = int(video_config['max_fps'])

system_config = config['SYSTEM']
# System config
MODEL_PATH = system_config['model_path']
ENABLE_LOGGING = system_config.getboolean('enable_logging')

processor = VideoProcessor(MODEL_PATH)

# Init JPEG encoder
jpeg_encoder = TurboJPEG()

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

origins = ["https://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def index(request: Request):
    """Serve the index HTML page.

    Args:
        request (Request): FastAPI request object.

    Returns:
        TemplateResponse: Rendered index.html template.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def get_stream(websocket: WebSocket):
    """WebSocket endpoint for streaming video frames and detection data.

    Processes video frames using the VideoProcessor and streams:
    - JPEG-encoded frames (binary data)
    - Detection objects with relevance scores (JSON)
    - GPS location (JSON, from stored task)
    - System metrics: CPU, memory usage (JSON, every 1 second)

    The stream continues until the client disconnects or video processing completes.

    Args:
        websocket (WebSocket): WebSocket connection to the client.
    """
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

            # New JPEG encoding
            jpeg_bytes = jpeg_encoder.encode(frame, quality=85)

            
            wrapped_objects = {"event": "objects", "content": objects}
            await websocket.send_text(json.dumps(wrapped_objects))
            await websocket.send_bytes(jpeg_bytes)
            
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
    # Disable WebSocket compression (ws_max_size default, but no per-message-deflate)
    uvicorn.run(
        app,
        host='127.0.0.1',
        port=8000,
        ws='websockets',  # Use websockets library (default)
        ws_per_message_deflate=False  # Disable compression to avoid zlib overhead
    )