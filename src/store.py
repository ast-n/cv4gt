"""Data Storage Module.

This module handles persistent storage of detection data, including:
- Saving frames with high-relevance objects (tagged with GPS and timestamp)
- Logging detection events to JSONL files
- Loading and caching UI assets (icons, images)

GPS coordinates are embedded in image EXIF data, and detection logs are
stored in line-delimited JSON format for efficient streaming and analysis.
"""

from __future__ import annotations

from PIL import Image
import camera_feed
import datetime
import numpy as np
import cv2
import json

tagged_folder_path = "/data/tagged"

def to_deg(value, loc):
    """Convert decimal GPS coordinates to degrees/minutes/seconds format.

    Args:
        value (float): GPS coordinate in decimal degrees.
        loc (list[str]): Two-element list of hemisphere indicators
            (e.g., ["S", "N"] for latitude or ["W", "E"] for longitude).

    Returns:
        tuple: (degrees, minutes, seconds, hemisphere) where:
            - degrees (int): Whole degrees
            - minutes (int): Whole minutes
            - seconds (float): Decimal seconds
            - hemisphere (str): Hemisphere indicator from loc parameter
    """
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
    """Tag image with GPS/timestamp and save to storage.

    Embeds GPS coordinates and timestamp in image EXIF data, then saves
    the image to the tagged folder with a timestamped filename.

    Args:
        image (PIL.Image.Image): Image to tag and store.

    Returns:
        str: Path to the saved image file.
    """
    
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
    """Get current GPS coordinates.

    Retrieves GPS location from the camera module.

    Returns:
        tuple[float, float]: GPS coordinates as (latitude, longitude).
            Falls back to (0, 0) if unavailable.
    """
    # Get current GPS location, probably from the camera.
    location = camera_feed.get_camera_gps()
    # Code to turn it into a tuple if thats not the format its given in.
    if location != None:
        return location
    else:
        return (0,0) # Decide on some fallback return.

async def store_image(image: Image.Image, img_exif: dict) -> str:
    """Save image with EXIF metadata to disk.

    Args:
        image (PIL.Image.Image): Image to save.
        img_exif (dict): EXIF metadata dictionary.

    Returns:
        str: Path to the saved image file.
    """
    now = datetime.datetime.now()
    filename = f"data/tagged/{str(datetime.date.today())}_{now.time().hour}-{now.time().minute}-{now.time().second}.{now.time().microsecond}.jpg"
    image.save(filename, exif=img_exif)
    return filename

stored_json = []
log_fileobject = None

def new_log(initial_data):
    """Create a new JSONL log file and write initial data.

    Args:
        initial_data (dict): Initial log entry to write.
    """
    global log_fileobject
    now = datetime.datetime.now()
    filename = f"data/logs/saved_log_{str(datetime.date.today())}_{now.time().hour}-{now.time().minute}-{now.time().second}.{now.time().microsecond}.jsonl"
    log_fileobject = open(filename, 'a', encoding='utf-8')
    jsonl_string = json.dumps(initial_data, ensure_ascii=False)
    log_fileobject.write(jsonl_string + "\n")

def create_new_element(new_frame_data, frame_num):
    """Create a formatted log entry for a frame's detections.

    Removes internal-only fields and adds detection numbering and timestamp.

    Args:
        new_frame_data (list[dict]): List of detection dictionaries.
        frame_num (int): Frame number.

    Returns:
        dict: Formatted log entry with frame_num, timestamp, and detections.
    """
    data = new_frame_data
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
    return total_data

def update_log(new_frame_data, frame_num):
    """Append detection data to the current log file.

    Args:
        new_frame_data (list[dict]): List of detection dictionaries.
        frame_num (int): Frame number.
    """
    new_data_text = create_new_element(new_frame_data, frame_num)
    global log_fileobject
    if log_fileobject is None:
        new_log(new_data_text)
    else:
        jsonl_string = json.dumps(new_data_text, ensure_ascii=False)
        log_fileobject.write(jsonl_string + "\n")

def save_and_close_log():
    """Close the current log file and save to disk."""
    global log_fileobject

    log_fileobject.close()
    print("Log file successfully saved")

def get_image(path: str) -> np.ndarray:
    """Load an image from disk using OpenCV.

    Args:
        path (str): Path to the image file.

    Returns:
        numpy.ndarray: Loaded image with all channels, or None if failed.
    """
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    return image

checkmark_image = None
cross_image = None

def get_grabber_indicator(indicator: str) -> np.ndarray | None:
    """Get cached UI indicator icon.

    Loads and caches checkmark/cross icons for bin gripper alignment display.

    Args:
        indicator (str): Indicator type - "check" or "cross".

    Returns:
        numpy.ndarray or None: Icon image with alpha channel, or None if invalid type.
    """
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
            