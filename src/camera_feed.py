""" CAMERA FEED """
""" This script should:
    - Handle receiving the camera feed.
    - Bundle camera feed into frames to find key ones.
    - Selecting key frames to send further down the pipeline.
    - Allow the camera to give GPS data upon request. """


class SingleFrame():
    def __init__(self):
        return NotImplementedError

def preprocess_raw_feed():
    return NotImplementedError

def get_key_frame():
    return NotImplementedError

def pipe_frame_to_processing():
    return NotImplementedError

def get_camera_gps():
    # Implement proper method once camera is connected.
    # For now, return coordinates from somewhere in Melbourne.
    location = (-37.814167, 144.963056)
    return location