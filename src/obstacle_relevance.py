# obstacle_relevance.py

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
        return 0
    # Subtract based on distance tiers
    elif depth >= 7.5:
        return max(base_rating - 2, 0)
    elif depth >= 5:
        return max(base_rating - 1, 0)
    else:
        return base_rating