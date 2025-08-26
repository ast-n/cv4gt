import camera_feed
import numpy as np

# Mapping each obstacle class to its relevance rating
RELEVANCE_RATING = {
    "person": 5,
    "adult": 5,
    "child": 5,
    "dog": 4,
    "cat": 4,
    "car": 4,
    "van": 4,
    "truck": 4,
    "motorbike": 5,
    "bicycle": 5,
    "person": 5,
    "cyclist_back": 5,
    "cyclist_front": 5, 
    "cyclist_side": 5,
    "head": 4,
    "helmet": 3,
    "sideloader_arm": 0,
    "fallen_bin": 4,
    "junk": 3,
    "bench": 2,
    "bin": 3,
    "shopping_cart": 2,
    "street_furniture": 3,
    "mailbox": 2,
    "bollard": 3,
    "pole": 3,
    "signpost": 2,
    "sign": 2,
    "power_box": 2,
    "power_pole": 3,
    "bus_shelter": 3,
    "tree": 3,
    "bird": 1,
    "boat": 1,
    "bottle": 1,
    "bus": 4,
    "chair": 1,
    "diningtable": 1,
    "horse": 4,
    "pottedplant": 1,
    "sheep": 3,
    "sofa": 1,
    "train": 4,
    "tvmonitor": 1,
    "aeroplane": 1
}

#the numbers are the average pixel sizes of the objects in the dataset
OBJECT_SCALE_MAP = {
    "person": 350,
    "adult": 350,
    "child": 250,
    "dog": 200,
    "cat": 150,
    "car": 1000,
    "van": 1500,
    "truck": 2000,
    "motorbike": 750,
    "bicycle": 600,
    "person": 350,
    "cyclist_back": 500,
    "cyclist_front": 500,
    "cyclist_side": 500,
    "head": 100,
    "helmet": 75,
    "sideloader_arm": 100,
    "fallen_bin": 300,
    "junk": 250,
    "bench": 350,
    "bin": 250,
    "shopping_cart": 400,
    "street_furniture": 500,
    "mailbox": 200,
    "bollard": 200,
    "pole": 400,
    "signpost": 500,
    "sign": 400,
    "power_box": 200,
    "power_pole": 400,
    "bus_shelter": 2000,
    "tree": 2500,
    "bird": 50,
    "boat": 2500,
    "bottle": 40,
    "bus": 3000,
    "chair": 150,
    "diningtable": 500,
    "horse": 750,
    "pottedplant": 150,
    "sheep": 400,
    "sofa": 500,
    "train": 4000,
    "tvmonitor": 150,
    "aeroplane": 10000
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

    if object_class == "sideloader_arm":
        return base_rating

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