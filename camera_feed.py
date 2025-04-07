""" CAMERA FEED """
""" This script should:
    - Handle receiving the camera feed.
    - Bundle camera feed into frames to find key ones.
    - Selecting key frames to send further down the pipeline."""


class SingleFrame():
    def __init__(self):
        return NotImplementedError

def preprocess_raw_feed():
    return NotImplementedError

def get_key_frame():
    return NotImplementedError

def pipe_frame_to_processing():
    return NotImplementedError