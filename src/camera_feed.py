""" CAMERA FEED
 This script should:
    - Handle receiving the camera feed from ZED.
    - Allow frame-by-frame retrieval to be synchronised across the project.
    - Provide access to depth and sensor data.
    - Allow the camera to give GPS data upon request. """

import pyzed.sl as sl
import numpy as np
import cv2

class ZEDCam:
    def __init__(self, recording_path:str=None, custom_model_onnx_path:str=None, masks:bool=False):
        self.zed = sl.Camera()
        self.grabbed_image = None
        
        init_params = sl.InitParameters()
        self.resolution = sl.RESOLUTION.HD720  # Start with HD720, can change
        init_params.camera_resolution = self.resolution
        self.fps = 30
        init_params.camera_fps = self.fps
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        init_params.coordinate_units = sl.UNIT.METER
        init_params.depth_mode = sl.DEPTH_MODE.NEURAL
        
        if recording_path:
            init_params.set_from_svo_file(recording_path)

        # Open camera
        err = self.zed.open(init_params)
        if (err != sl.ERROR_CODE.SUCCESS):
            print("Error in opening ZED camera.")
            raise Exception()
        
        # Enable position tracking
        py_transform = sl.Transform()
        tracking_parameters = sl.PositionalTrackingParameters(_init_pos=py_transform)
        err = self.zed.enable_positional_tracking(tracking_parameters)
        if (err != sl.ERROR_CODE.SUCCESS):
            self.zed.close()
            print("Error in enabling positional tracking.")
            raise Exception()
        
        # Define the object detection parameters
        obj_param = sl.ObjectDetectionParameters()
        obj_param.enable_tracking=True
        
        self.masks = masks
        if self.masks:
            obj_param.enable_mask_output=True
            
        if custom_model_onnx_path:
            obj_param.custom_onnx_file = custom_model_onnx_path
            obj_param.detection_model = sl.OBJECT_DETECTION_MODEL.CUSTOM_YOLOLIKE_BOX_OBJECTS
        else:
            obj_param.detection_model = sl.OBJECT_DETECTION_MODEL.CUSTOM_BOX_OBJECTS
        
        err = self.zed.enable_object_detection(obj_param)
        if err != sl.ERROR_CODE.SUCCESS :
            self.zed.close()
            print("Error in enabling object tracking.")
            raise Exception()
        
        # Set up runtime parameters
        self.runtime_parameters = sl.RuntimeParameters()
        self.runtime_parameters.enable_depth = True
        self.runtime_parameters.confidence_threshold = 10
        
        self.zed_sensors = sl.SensorsData()
        
        self.obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
        
        self.objects = sl.Objects()
        self.image_mat = sl.Mat(mat_type=sl.MAT_TYPE.U8_C4)
        self.depth_mat = sl.Mat(mat_type=sl.MAT_TYPE.F32_C1)
    
    def prepare_frame(self):
        grab_status = self.zed.grab(self.runtime_parameters)
        if grab_status != sl.ERROR_CODE.SUCCESS:
            self.shutdown()
            print("Error grabbing frame from ZED camera.")
            raise Exception()
        
    def get_image(self):
        self.zed.retrieve_image(self.image_mat, sl.VIEW.LEFT)
        frame_bgr_a = self.image_mat.get_data()

        current_frame_for_cv = None
        if frame_bgr_a is not None and isinstance(frame_bgr_a, np.ndarray):
            # Ensure it's a copy and BGR
            copied_frame = frame_bgr_a.copy()
            if copied_frame.shape[2] == 4:
                current_frame_for_cv = cv2.cvtColor(copied_frame, cv2.COLOR_BGRA2BGR)
            elif copied_frame.shape[2] == 3:
                current_frame_for_cv = copied_frame
            else:
                print(f"Unexpected channels from ZED frame: {copied_frame.shape[2]}")
                self.shutdown()
                raise Exception()
        else:
            print("ZED frame is in invalid format or null.")
            self.shutdown()
            raise Exception()
        
        if current_frame_for_cv is None:
            print("Failed to retrieve valid data from ZED frame.")
            self.shutdown()
            raise Exception()
        
        return current_frame_for_cv
    
    def get_depth_map(self):
        self.zed.retrieve_measure(self.depth_mat, measure=sl.MEASURE.DEPTH)
        depth_image = self.depth_mat.get_data()
        
        if depth_image is not None and isinstance(depth_image, np.ndarray):
            pass
        else:
            print("Retrieved depth map is in invalid format or null.")
            self.shutdown()
            raise Exception()
        
        return depth_image
    
    def get_depth_display(self):
        self.zed.retrieve_image(self.depth_mat, view=sl.VIEW.DEPTH)
        depth_image = self.depth_mat.get_data()
        
        if depth_image is not None and isinstance(depth_image, np.ndarray):
            pass
        else:
            print("Retrieved depth map is in invalid format or null.")
            self.shutdown()
            raise Exception()
        
        return depth_image
    
    def get_gps(self):
        # We don't have a GPS/GNSS module connected to our ZED camera right now, so we will just return a temporary value.
        location = (-37.814167, 144.963056)
        return location
    
    def track_object_detections(self, det_objects:list):
        self.zed.ingest_custom_box_objects(det_objects)
        
        self.zed.retrieve_objects(self.objects, self.obj_runtime_param)
        
        return self.objects.object_list
    
    def get_resolution(self):
        resolution = sl.get_resolution(self.resolution)
        return (resolution.width, resolution.height)
    
    def get_fps(self):
        return self.fps
    
    def shutdown(self):
        self.zed.disable_object_detection()
        self.zed.close()
            
            
# -------------------------------------------------------------------------------------------------------------------------------------------------------
            
zed_cam = None

def setup_cam(recording_path:str=None, custom_model_onnx_path:str=None, masks:bool=False):
    """
        Initialises the ZED camera or simulated camera from a recording.
    """
    
    global zed_cam
    zed_cam = ZEDCam(recording_path, custom_model_onnx_path, masks)

def go_next_frame():
    """
        Prepares the data for the next frame from the ZED camera.\n
        Always call this method once before calling all of the get_ methods.\n
        e.g.:
        \n
            camera_feed.setup_cam()
            
            while True:
                camera_feed.go_next_frame()
                input_image = camera_feed.get_image()
                input_depth = camera_feed.get_depth_map()
                
                ...
        
    """
    
    global zed_cam
    zed_cam.prepare_frame()

def get_image() -> np.ndarray|None:
    """
        Method to retrieve the image data of the current frame.\n
        Returns: np.ndarray in BGR format, usable by opencv.
    """
    
    global zed_cam
    im = zed_cam.get_image()
    return im

def get_depth_map() -> np.ndarray|None:
    """
        Method to retrieve the depth map of the current frame.\n
        Returns: single-channel np.ndarray of the same dimensions as the current frame.
    """
    
    global zed_cam
    depth_im = zed_cam.get_depth_map()
    return depth_im

def get_depth_display() -> np.ndarray|None:
    """
        Method to retrieve the depth map in a special normalised form for visual output.\n
        Returns: single-channel np.ndarray of depth data\n
        \n
        NEVER USE THIS DATA TO PERFORM A FUNCTION OTHER THAN VISUAL DISPLAY
    """
    
    global zed_cam
    depth_im = zed_cam.get_depth_display()
    return depth_im

def get_camera_gps() -> tuple:
    """
        Method to retrieve the GPS location associated with the current frame.\n
        Returns: Tuple of signed (lat,lng) along N and E axes.
        
        CURRENTLY RETURNS A TEMPORARY VALUE
    """
    
    global zed_cam
    gps_loc = zed_cam.get_gps()
    return gps_loc

def track_object_detections(detections:list) -> list:
    """
        Method to retrieve object detections, tracking, positions, movement, etc for the current frame.
        Returns a list of dictionaries, which each dict holding information for each object present.
        
        NOT CURRENTLY IMPLEMENTED
    """
    
    temp_class_dict = {}
    
    det_objects = []
    det_tracking_ids = []
    
    for det in detections:
        tmp = sl.CustomBoxObjectData()
        tmp.unique_object_id = sl.generate_unique_id()
        det_tracking_ids.append(tmp.unique_object_id)
        tmp.probability = det['confidence']
        tmp.label = int(det['class_id'])
        bbox = det['bbox']
        tmp.bounding_box_2d = np.array([[bbox[0], bbox[1]], [bbox[2], bbox[1]], [bbox[0], bbox[3]], [bbox[2], bbox[3]]])
        tmp.is_grounded = True
        det_objects.append(tmp)
        temp_class_dict[tmp.label] = det['class']

    global zed_cam
    track_objects = zed_cam.track_object_detections(det_objects)
    
    track_list = []
    for obj in track_objects:
        obj_track_id = obj.unique_object_id
        if obj_track_id not in det_tracking_ids:
            continue
        obj_class_id = obj.raw_label
        if obj_class_id not in temp_class_dict.keys():
            continue
        obj_velocity = obj.velocity
        obj_bbox_2d = [obj.bounding_box_2d[0][0], obj.bounding_box_2d[0][1], obj.bounding_box_2d[1][0], obj.bounding_box_2d[2][1]]
        obj_centre = list(((obj_bbox_2d[0]+obj_bbox_2d[2])/2, (obj_bbox_2d[1]+obj_bbox_2d[3])/2))
        obj_confidence = obj.confidence
        obj_mask = obj.mask
        
        track_list.append({
            'class': temp_class_dict[obj_class_id],
            'class_id': obj_class_id,
            'track_id': obj_track_id,
            'confidence': obj_confidence,
            'bbox': obj_bbox_2d,
            'centre': obj_centre,
            'mask': obj_mask,
            'velocity': obj_velocity
        })
    
    return track_list

def get_zed_resolution() -> tuple:
    """
        Method to retrieve the resolution of the currently connected ZED camera or recording.
    """
    
    global zed_cam
    resolution = zed_cam.get_resolution()
    return resolution

def get_zed_fps() -> int:
    """
        Method to retrieve the FPS of the currently connected ZED camera or recording.
    """
    
    global zed_cam
    fps = zed_cam.get_fps()
    return fps

def shutdown_cam():
    """
        Method to call to ensure proper shutdown of the ZED camera reading pipeline.
    """
    global zed_cam
    zed_cam.shutdown()
    
