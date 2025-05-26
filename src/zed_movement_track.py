"""
    Script for testing movement tracking with the ZED camera.
"""

import pyzed.sl as sl
import numpy as np

zed = sl.Camera()

init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.AUTO
init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
init_params.coordinate_units = sl.UNIT.METER

# Open camera
err = zed.open(init_params)
if (err != sl.ERROR_CODE.SUCCESS):
    exit(-1)


# Enable position tracking
py_transform = sl.Transform()
tracking_parameters = sl.PositionalTrackingParameters(_init_pos=py_transform)
err = zed.enable_positional_tracking(tracking_parameters)
if (err != sl.ERROR_CODE.SUCCESS):
    zed.close()
    exit(-1)


i = 0
zed_pose = sl.Pose()

zed_sensors = sl.SensorData()
runtime_parameters = sl.RuntimeParameters()

movement_history = np.array([])
time_history = np.array([])

while i < 3600: # Run for 3600 frames (60 seconds)
    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)

        # Display the translation and timestamp
        py_translation = sl.Translation()
        translation_array = zed_pose.get_translation(py_translation).get()
        
        curr_time = zed_pose.timestamp.get_milliseconds()
        
        # Velovity = movement/time
        # Probably don't want velocity to be based on just one frame though so record some history.
        movement_history = np.vstack((movement_history, translation_array))
        if movement_history.shape[0] > 5:
            movement_history = movement_history[-5:] # Only keep 5 most recent values
        
        time_history = np.append(time_history, curr_time)
        if time_history.size > 5:
            time_history = time_history[-5:]
        
        velocity = np.sum(movement_history, axis=0) / np.sum(time_history) # Output should be 3-dim vector of velocity along x, y, z.
        
        
        print(f"Velocity: {velocity}, Timestamp: {curr_time}\n")
        
        # Should also add a way to account for rotation
        # The camera does track this but its with quaternions which are uh yeah...