from __future__ import annotations
""" IMAGE PROCESSING """
""" This script should:
    - Take in key frames. 
    - Run data pre-processing for the AI.
    - Send images to the object-recognition module.
    - Process prediction results from the object-recognition module.
    - Send frames off to be GPS tagged.
    - Find bounds of detected hazards."""


class InputQueue():
    def __init__(self):
        return NotImplementedError

def preprocess_image():
    return NotImplementedError

def send_to_object_detection():
    return NotImplementedError

def send_to_tag():
    return NotImplementedError

def get_bounds():
    return NotImplementedError
