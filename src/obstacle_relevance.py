import camera_feed
import numpy as np

# Mapping each obstacle class to its relevance rating
RELEVANCE_RATING = {
    "person": 5,
    "cyclist": 5,
    "fallen_bin": 4,
    "animal": 4,
    "vehicle": 4,
    "ground_hazard": 3,
    "bin": 3,
    "fixed_obstacle": 3
}

# The numbers are the average pixel sizes of the objects in the dataset
# Used for depth estimation when RealSense depth map is unavailable
OBJECT_SCALE_MAP = {
    "person": 350, 
    "cyclist": 500,
    "vehicle": 1500,
    "fallen_bin": 300,
    "bin": 250,
    "animal": 200,
    "fixed_obstacle": 400,
    "ground_hazard": 200
}


MAX_DEPTH = 15 # Maximum depth in meters for depth estimation

def get_obstacle_relevance_rating(object_class:str, depth:float, velocity:float) -> int:
    """
    Returns the relevance rating for a given object class, adjusted by depth.
    
    Args:
        object_class (str): The class of the detected object.
        depth (float): The depth/distance to the object in meters.
    
    Returns:
        int: The adjusted relevance rating for the object.
    """
    base_rating = RELEVANCE_RATING.get(object_class, 1)
    rating = base_rating
    
    # Cull anything ≥ max depth — too far to be hazardous
    if depth >= MAX_DEPTH:
        return 0
    
    if depth >= 7:
        rating -= 4
    elif depth >= 5:
        rating -= 2
    elif depth >= 3:
        rating -= 1
        
    if 0.6 < velocity < 10: # Max value set because velocity is misinterpreted as some incredibly high value sometimes. 10m/s = 36km/hr.
        rating += 2
        
    return max(0, min(rating, 5))

def estimate_depth(object_class:str, bbox):
    """
    Estimates the depth of an object based on the bounding box area
    using a square root inverse area model.
    """
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1
    area = width * height
    if area <= 0:
        return MAX_DEPTH

    object_scale = OBJECT_SCALE_MAP.get(object_class, 1.0)  # in meters
    depth = object_scale / (area ** 0.5)  # square root inverse area

    return depth

def real_depth(bbox, depth_map):
    x1, y1, x2, y2 = map(int, bbox)
    if x2 <= x1 or y2 <= y1 or depth_map is None:
        return MAX_DEPTH
    
    # Find depth in bounding
    bbox_depths_mm = depth_map[y1:y2, x1:x2]

    # Convert to meters
    valid_depths_m = bbox_depths_mm[bbox_depths_mm > 0].astype(np.float32) / 1000.0

    # Filter
    valid_depths_in_range = valid_depths_m[valid_depths_m < MAX_DEPTH]

    if valid_depths_in_range.size == 0:
        return MAX_DEPTH

    # Calculate the median of the valid, in-range depth values
    median_depth = np.median(valid_depths_in_range)
    
    return float(median_depth)

def get_object_median_depths(objects:list, depth_map: np.ndarray | None) -> list:
    """
        Takes in a list of objects then returns the same list with depths calculated and attached to them.
    """
    for obj in objects:    
        # Real Depth first
        if depth_map is not None:
            real_d = real_depth(obj['bbox'], depth_map)
            
            if real_d < MAX_DEPTH:
                obj['depth'] = real_d
            else:
                obj['depth'] = MAX_DEPTH
        else:
            obj['depth'] = estimate_depth(obj['class'], obj['bbox'])
            
    return objects