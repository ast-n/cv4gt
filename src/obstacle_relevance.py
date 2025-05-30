# Mapping each obstacle class to its relevance rating
RELEVANCE_RATING = {
    "adult": 5,
    "child": 5,
    "dog": 4,
    "cat": 4,
    "car": 5,
    "van": 5,
    "truck": 5,
    "motorbike": 5,
    "bicycle": 5,
    "person": 5,
    "cyclist_back": 5,
    "cyclist_front": 5, 
    "cyclist_side": 5,
    "head": 4,
    "helmet": 3,
    "sideloader_arm": 1,
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

MAX_DEPTH = 10 # Maximum depth in meters for depth estimation

def get_obstacle_relevance_rating(object_class: str, depth: float) -> int:
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

    # Cull anything ≥ 10m — too far to be hazardous
    if depth >= 10:
        return max(base_rating - 4, 0)
    # Subtract based on distance tiers
    elif depth >= 5:
        return max(base_rating - 2, 0)
    elif depth >= 3:
        return max(base_rating - 1, 0)
    else:
        return base_rating

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