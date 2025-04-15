from __future__ import annotations
""" STORE """
""" This script should:
    - Handle storage, stowing, and retrieval of any data in long-term storage.
    - Tag hazard frames with GPS and time then store them.
    - Storage of any other permanent files which the codebase needs access to (config, maybe frontend files, etc.)"""

from PIL import Image
from camera_feed import get_camera_gps
import datetime

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


def tag_and_store(image: Image.Image) -> str:
    
    GPS_INFO_TAG = 34853
    
    current_gps = get_gps()
    
    lat_deg = to_deg(current_gps[0], ["S", "N"])
    lng_deg = to_deg(current_gps[1], ["W", "E"])
    
    exiv_lat = (lat_deg[0],lat_deg[1],lat_deg[2])
    exiv_lng = (lng_deg[0],lng_deg[1],lng_deg[2])
    
    image_exif = image.getexif()
    
    gps_tags = [1, 2, 3, 4] # latRef, Lat, LongRef, Long
    
    exif_dict = {GPS_INFO_TAG : dict(zip(gps_tags, [lat_deg[3], exiv_lat, lng_deg[3], exiv_lng]))}
    
    image_exif.update(exif_dict)
    
    filename = store_image(image, image_exif)
    
    return filename

def get_gps() -> tuple:
    # Get current GPS location, probably from the camera.
    location = get_camera_gps()
    # Code to turn it into a tuple if thats not the format its given in.
    if location != None:
        return location
    else:
        return (0,0) # Decide on some fallback return.

def store_image(image: Image.Image, img_exif: dict) -> str:
    now = datetime.datetime.now()
    filename = f"data/tagged/{str(datetime.date.today())}_{now.time().hour}-{now.time().minute}-{now.time().second}.{now.time().microsecond}.jpg"
    image.save(filename, exif=img_exif)
    return filename

def get_image():
    return NotImplementedError

def get_model():
    return NotImplementedError

def save_model():
    return NotImplementedError

def get_file():
    return NotImplementedError

def save_file():
    return NotImplementedError