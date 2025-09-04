from __future__ import annotations
""" STORE
This script should:
    - Handle storage, stowing, and retrieval of any data in long-term storage.
    - Tag hazard frames with GPS and time then store them.
    - Storage of any other permanent files which the codebase needs access to (config, maybe frontend files, etc.)"""

from PIL import Image
import camera_feed
import datetime
import numpy as np
import cv2
import json

tagged_folder_path = "/data/tagged"

def to_deg(value, loc):
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60,5)
    return (deg, min, sec, loc_value)


async def tag_and_store(image: Image.Image) -> str:
    
    GPS_INFO_TAG = 34853
    
    current_gps = await get_gps()
    
    lat_deg = to_deg(current_gps[0], ["S", "N"])
    lng_deg = to_deg(current_gps[1], ["W", "E"])
    
    exiv_lat = (lat_deg[0],lat_deg[1],lat_deg[2])
    exiv_lng = (lng_deg[0],lng_deg[1],lng_deg[2])
    
    image_exif = image.getexif()
    
    gps_tags = [1, 2, 3, 4] # latRef, Lat, LongRef, Long
    
    exif_dict = {GPS_INFO_TAG : dict(zip(gps_tags, [lat_deg[3], exiv_lat, lng_deg[3], exiv_lng]))}
    
    image_exif.update(exif_dict)
    
    filename = await store_image(image, image_exif)
    
    return filename

async def get_gps() -> tuple:
    # Get current GPS location, probably from the camera.
    location = camera_feed.get_camera_gps()
    # Code to turn it into a tuple if thats not the format its given in.
    if location != None:
        return location
    else:
        return (0,0) # Decide on some fallback return.

async def store_image(image: Image.Image, img_exif: dict) -> str:
    now = datetime.datetime.now()
    filename = f"data/tagged/{str(datetime.date.today())}_{now.time().hour}-{now.time().minute}-{now.time().second}.{now.time().microsecond}.jpg"
    image.save(filename, exif=img_exif)
    return filename

stored_json = []

def add_to_log(new_frame_date, frame_num):
    data = new_frame_date
    det_num = 0
    for item in data:
        if "class_id" in item:
            del item["class_id"]
        if "centre" in item:
            del item["centre"]
        if "mask_polygon_norm" in item:
            del item["mask_polygon_norm"]
        item['detection_num'] = det_num
        det_num += 1
        
    now = datetime.datetime.now()
    total_data = {"frame_num": frame_num, "timestamp": f"{str(datetime.date.today())}_{now.time().hour}-{now.time().minute}-{now.time().second}.{now.time().microsecond}", "detections": data}
    global stored_json
    stored_json.append(total_data)

def save_and_close_log():
    global stored_json
    now = datetime.datetime.now()
    filename = f"data/logs/saved_log_{str(datetime.date.today())}_{now.time().hour}-{now.time().minute}-{now.time().second}.{now.time().microsecond}.json"
    current_log = open(filename, 'w', encoding='utf-8')
    
    json.dump(stored_json, current_log, ensure_ascii=False, indent=4)
    
    current_log.close()
    print("Log file successfully saved")

def get_image(path:str) -> np.ndarray:
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    return image

checkmark_image = None
cross_image = None

def get_grabber_indicator(indicator:str) -> np.ndarrray | None:
    match indicator:
        case "check":
            global checkmark_image
            if checkmark_image is None:
                checkmark_image = get_image("data/UI/check.png")
            return checkmark_image
        case "cross":
            global cross_image
            if cross_image is None:
                cross_image = get_image("data/UI/cancel.png")
            return cross_image
        case _:
            return None
            

def get_model():
    return NotImplementedError

def save_model():
    return NotImplementedError

def get_file():
    return NotImplementedError

def save_file():
    return NotImplementedError