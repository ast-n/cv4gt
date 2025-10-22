"""Camera Feed Module.

This module provides an interface to Intel RealSense cameras for capturing
color images and depth maps. It supports both live camera feeds and playback
from recorded .bag files.

The module uses a global singleton pattern for easy access across the project,
with setup/teardown functions and a RealSenseCam class that handles the
pyrealsense2 pipeline configuration and frame alignment.
"""

import numpy as np
import pyrealsense2 as rs

class RealSenseCam:
    """Intel RealSense camera interface.

    Manages the RealSense pipeline for capturing aligned color and depth frames.
    Supports both live camera streaming and playback from recorded .bag files.

    Attributes:
        pipeline (rs.pipeline): RealSense pipeline for frame capture.
        config (rs.config): Pipeline configuration.
        profile (rs.pipeline_profile): Active pipeline profile after start.
        align (rs.align): Frame alignment object to align depth to color.
    """
    def __init__(self, recording_path=None, resolution=(640, 480), fps=30):
        """Initialise RealSense camera.

        Args:
            recording_path (str, optional): Path to .bag file for playback. If None,
                uses live camera feed.
            resolution (tuple[int, int], optional): Camera resolution as (width, height).
                Defaults to (640, 480).
            fps (int, optional): Frame rate in frames per second. Defaults to 30.
        """
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
        """Get next frame set from the camera.

        Retrieves the next available frameset and aligns depth to color.

        Returns:
            tuple: (aligned_frames, success) where:
                - aligned_frames (rs.composite_frame): Aligned frameset, or None if failed
                - success (bool): True if frames retrieved successfully, False otherwise
        """
        success, frames = self.pipeline.try_wait_for_frames()
        if not success:
            return None, None

        aligned_frames = self.align.process(frames)
        return aligned_frames, True

    def get_image(self, aligned_frames):
        """Extract color image from aligned frames.

        Args:
            aligned_frames (rs.composite_frame): Aligned frameset from get_frames().

        Returns:
            numpy.ndarray or None: Color image as RGB array, or None if no color frame.
        """
        color_frame = aligned_frames.get_color_frame()
        if not color_frame:
            return None
        return np.asanyarray(color_frame.get_data())

    def get_depth_map(self, aligned_frames):
        """Extract depth map from aligned frames.

        Args:
            aligned_frames (rs.composite_frame): Aligned frameset from get_frames().

        Returns:
            numpy.ndarray or None: Depth map in millimeters as uint16 array, or None
                if no depth frame.
        """
        depth_frame = aligned_frames.get_depth_frame()
        if not depth_frame:
            return None
        return np.asanyarray(depth_frame.get_data())

    def get_resolution(self):
        """Get current color stream resolution.

        Returns:
            tuple[int, int]: Resolution as (width, height).
        """
        color_profile = self.profile.get_stream(rs.stream.color).as_video_stream_profile()
        return (color_profile.width(), color_profile.height())

    def get_fps(self):
        """Get current color stream frame rate.

        Returns:
            int: Frame rate in frames per second.
        """
        return self.profile.get_stream(rs.stream.color).fps()

    def shutdown(self):
        """Stop the RealSense pipeline and release resources."""
        self.pipeline.stop()

# Global singleton instance
realsense_cam = None

def setup_cam(recording_path=None, resolution=(640, 480), fps=30):
    """Initialise the global RealSense camera instance.

    Args:
        recording_path (str, optional): Path to .bag file for playback.
        resolution (tuple[int, int], optional): Camera resolution. Defaults to (640, 480).
        fps (int, optional): Frame rate. Defaults to 30.
    """
    global realsense_cam
    realsense_cam = RealSenseCam(recording_path, resolution, fps)

def get_frames():
    """Get next frame set from the global camera instance.

    Returns:
        tuple: (aligned_frames, success) from RealSenseCam.get_frames().
    """
    global realsense_cam
    return realsense_cam.get_frames()

def get_image(aligned_frames):
    """Extract color image from aligned frames.

    Args:
        aligned_frames (rs.composite_frame): Aligned frameset.

    Returns:
        numpy.ndarray or None: Color image as RGB array.
    """
    global realsense_cam
    return realsense_cam.get_image(aligned_frames)

def get_depth_map(aligned_frames):
    """Extract depth map from aligned frames.

    Args:
        aligned_frames (rs.composite_frame): Aligned frameset.

    Returns:
        numpy.ndarray or None: Depth map in millimeters.
    """
    global realsense_cam
    return realsense_cam.get_depth_map(aligned_frames)

def get_camera_gps():
    """Get GPS coordinates from camera.

    Note:
        Currently returns a placeholder location @ Swinburne.

    Returns:
        tuple[float, float]: GPS coordinates as (latitude, longitude).
    """
    return (-37.814167, 144.963056) # Placeholder

def shutdown_cam():
    """Shutdown the global camera instance and release resources."""
    global realsense_cam
    if realsense_cam is not None:
        realsense_cam.shutdown()
        realsense_cam = None