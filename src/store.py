from __future__ import annotations
""" STORE """
""" This script should:
    - Handle storage, stowing, and retrieval of any data in long-term storage.
    - Tag hazard frames with GPS and time then store them.
    - Storage of any other permanent files which the codebase needs access to (config, maybe frontend files, etc.)"""


import pyexiv2.convert
import pyexiv2.lib
import pyexiv2.reference #Better type hints
from PIL import Image, ExifTags
from camera_feed import get_camera_gps
import datetime
import exif
import pyexiv2
import fractions
from numbers import Rational

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
    print(deg, min, sec, loc_value)
    return (deg, min, sec, loc_value)


def tag_and_store(image: Image.Image) -> str:
    
    filename = store_image(image)
    
    current_gps = get_gps()
    
    lat_deg = to_deg(current_gps[0], ["S", "N"])
    lng_deg = to_deg(current_gps[1], ["W", "E"])
    
    # No, this code doesn't make sense. Yes, this is the only way it works. I don't even know. It took me 5 hours to make this work correctly.
    exiv_lat = (0,0,(lat_deg[0],lat_deg[1],lat_deg[2]))
    exiv_lng = (0,0,(lng_deg[0],lng_deg[1],lng_deg[2]))
    
    exiv_image = pyexiv2.Image(filename)
    exiv_image.read_exif()
    
    exif_dict = {
        "Exif.GPSInfo.GPSLatitude" : exiv_lat,
        "Exif.GPSInfo.GPSLatitude" : exiv_lat,
        "Exif.GPSInfo.GPSLatitudeRef" : lat_deg[3],
        "Exif.GPSInfo.GPSLongitude" : exiv_lng,
        "Exif.GPSInfo.GPSLongitudeRef" : lng_deg[3],
        "Exif.Image.GPSTag" : 654
    }
    
    exiv_image.modify_exif(exif_dict)
    exiv_image.close()
    
    return filename

def get_gps() -> tuple:
    # Get current GPS location, probably from the camera.
    location = get_camera_gps()
    # Code to turn it into a tuple if thats not the format its given in.
    if location != None:
        return location
    else:
        return (0,0) # Decide on some fallback return.

def store_image(image: Image.Image) -> str:
    now = datetime.datetime.now()
    filename = f"data/tagged/{str(datetime.date.today())}_{now.time().hour}-{now.time().minute}-{now.time().second}.{now.time().microsecond}.jpg"
    image.save(filename)
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