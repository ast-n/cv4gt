"""Obstacle Relevance Scoring Module.

This module provides functionality for assessing the relevance/danger level of
detected obstacles based on their class, distance (depth), and velocity.
Calculates both real depth from RealSense depth maps and estimated depth from
bounding box size when depth data is unavailable.

The relevance scoring system uses a 1-5 scale where 5 is highest priority
(immediate danger) and 1 is lowest priority (distant or low-risk objects).
"""

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

def get_obstacle_relevance_rating(object_class: str, depth: float, velocity: float) -> int:
    """Calculate dynamic relevance rating for a detected object.

    Computes a relevance score (1-5) based on object class, distance, and velocity.
    The base rating comes from the object class, which is then adjusted down for
    greater distances and up for moving objects.

    Distance penalties:
        - ≥7m: -4 to rating
        - ≥5m: -2 to rating
        - ≥3m: -1 to rating

    Velocity bonus:
        - 0.6-10 m/s: +2 to rating

    Args:
        object_class (str): The class of the detected object (e.g., "person", "bin").
        depth (float): The depth/distance to the object in meters.
        velocity (float): The object's velocity in meters per second.

    Returns:
        int: The adjusted relevance rating from 0-5, where:
            - 5: Highest priority (immediate danger)
            - 4: High priority
            - 3: Medium priority
            - 2: Low priority
            - 1: Very low priority
            - 0: Filtered out (too far or irrelevant)
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

def estimate_depth(object_class: str, bbox):
    """Estimate object depth from bounding box size.

    Uses an inverse square root relationship between bounding box area and
    distance to estimate depth when RealSense depth data is unavailable.
    Each object class has a calibrated scale factor based on average real-world
    sizes from the training dataset.

    Formula: depth = object_scale / sqrt(bbox_area)

    Args:
        object_class (str): The class of the detected object.
        bbox (list[float]): Bounding box as [x1, y1, x2, y2].

    Returns:
        float: Estimated depth in meters, or MAX_DEPTH if area is invalid.
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
    """Calculate real depth from RealSense depth map.

    Extracts depth values from the RealSense depth map within the bounding box,
    filters out invalid readings, and returns the median depth.

    Args:
        bbox (list[float]): Bounding box as [x1, y1, x2, y2].
        depth_map (numpy.ndarray or None): RealSense depth map in millimeters,
            or None if unavailable.

    Returns:
        float: Median depth in meters within the bounding box, or MAX_DEPTH if
            no valid depth data is available.
    """
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

def get_object_median_depths(objects: list, depth_map: np.ndarray | None) -> list:
    """Add depth information to detected objects.

    Processes a list of detected objects and adds 'depth' field to each using
    either real depth from RealSense depth map (preferred) or estimated depth
    from bounding box size (fallback).

    Args:
        objects (list[dict]): List of detected objects, each with 'bbox' and 'class' fields.
        depth_map (numpy.ndarray or None): RealSense depth map in millimeters, or None.

    Returns:
        list[dict]: Same list of objects with 'depth' (float) field added to each,
            representing distance in meters.
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