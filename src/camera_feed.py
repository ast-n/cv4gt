""" CAMERA FEED
 This script should:
    - Handle receiving the camera feed from RealSense.
    - Allow frame-by-frame retrieval to be synchronised across the project.
    - Provide access to depth and sensor data.
    - Allow the camera to give GPS data upon request. """

import numpy as np
import pyrealsense2 as rs

class RealSenseCam:
    def __init__(self, recording_path=None, resolution=(640, 480), fps=30):
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        if recording_path:
            self.config.enable_device_from_file(recording_path, repeat_playback=True)
        else:
            # Add streams to configuration
            self.config.enable_stream(rs.stream.depth, resolution[0], resolution[1], rs.format.z16, fps)
            self.config.enable_stream(rs.stream.color, resolution[0], resolution[1], rs.format.bgr8, fps)

        # Start stream
        self.profile = self.pipeline.start(self.config)

        if recording_path:
            # Set playback to not be in real-time
            playback = self.profile.get_device().as_playback()
            playback.set_real_time(False)

        # Alignment (depth to colour) -> for distance might be important
        self.align = rs.align(rs.stream.color)

    def get_frames(self):
        success, frames = self.pipeline.try_wait_for_frames()
        if not success:
            return None, None
        
        aligned_frames = self.align.process(frames)
        return aligned_frames, True

    def get_image(self, aligned_frames):
        color_frame = aligned_frames.get_color_frame()
        if not color_frame:
            return None
        return np.asanyarray(color_frame.get_data())

    def get_depth_map(self, aligned_frames):
        depth_frame = aligned_frames.get_depth_frame()
        if not depth_frame:
            return None
        return np.asanyarray(depth_frame.get_data())

    def get_resolution(self):
        color_profile = self.profile.get_stream(rs.stream.color).as_video_stream_profile()
        return (color_profile.width(), color_profile.height())

    def get_fps(self):
        return self.profile.get_stream(rs.stream.color).fps()

    def shutdown(self):
        self.pipeline.stop()

# -------------------------------------------------------------------------------------------------------------------------------------------------------
            
realsense_cam = None

def setup_cam(recording_path=None, resolution=(640, 480), fps=30):
    global realsense_cam
    realsense_cam = RealSenseCam(recording_path, resolution, fps)

def get_frames():
    global realsense_cam
    return realsense_cam.get_frames()

def get_image(aligned_frames):
    global realsense_cam
    return realsense_cam.get_image(aligned_frames)

def get_depth_map(aligned_frames):
    global realsense_cam
    return realsense_cam.get_depth_map(aligned_frames)

def get_camera_gps():
    return (-37.814167, 144.963056) # Placeholder

def shutdown_cam():
    global realsense_cam
    if realsense_cam is not None:
        realsense_cam.shutdown()
        realsense_cam = None