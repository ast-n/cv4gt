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
    "tree": 3
}

def get_obstacle_relevance_rating(object_class: str) -> int:
    """
    Returns the relevance rating for a given object class.
    
    Args:
    - object_class (str): The class of the detected object.
    
    Returns:
    - int: The relevance rating for the object class.
    """
    return RELEVANCE_RATING.get(object_class, 1)  # Default to 1 if not found
