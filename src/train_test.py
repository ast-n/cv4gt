""" TRAIN/TEST """
""" This script should:
    - Be used for training and finetuning models during development.
    - Be used for evaluating AI models alone.
    - Be used testing new techniques in regards to the AI models.
    - Be used for testing various things that need testing."""

import store
from PIL import Image
from roboflow import Roboflow
import os
import shutil
from datetime import datetime
from glob import glob


# ===================== SETUP =====================

def test_gps_tag():
    test_image = Image.open("data/test.jpg")

    saved = store.tag_and_store(test_image)

    check_image = Image.open(saved)
    print(check_image.getexif())

# ===================== TRAIN =====================

def get_dataset_path():
    """
    Function to setup paths for subsequent functions
    """
    today_str =  datetime.today().strftime("%d-%m")
    dataset_name = f"cv4gt-data-{today_str}"
    dataset_yaml_path = os.path.join("data", "training", dataset_name, "data.yaml")
    return dataset_yaml_path, dataset_name

def train_model(epochs):
    """
    Function to train model
    """
    data_yaml_path, dataset_name = get_dataset_path()
    print(f"Using dataset configuration: {data_yaml_path}")
    print(f"Dataset name identifier: {dataset_name}")

    yolo_command = f"yolo task=detect mode=train model=yolov8x data={data_yaml_path} epochs={epochs} imgsz=640 save_period=50"

    print(f"Running: {yolo_command}")
    os.system(yolo_command)
    
def save_model(epochs):
    """
    Function to handle saving best weight to /models
    """
    _, dataset_name = get_dataset_path()
    detect_runs = sorted(glob("runs/detect/train*"), key=os.path.getmtime, reverse=True)

    if not detect_runs:
        print("No training runs found in runs/detect/")
        return

    latest_run = detect_runs[0]
    best_model_path = os.path.join(latest_run, "weights", "best.pt")

    if not os.path.exists(best_model_path):
        print(f"best.pt not found at {best_model_path}")
        return

    os.makedirs("models", exist_ok=True)
    clean_dataset_name = dataset_name.replace(" ", "_").replace("(", "").replace(")", "")
    output_model_name = f"YOLOv8-{clean_dataset_name}_{epochs}e.pt"
    output_model_path = os.path.join("models", output_model_name)

    shutil.copy(best_model_path, output_model_path)
    print(f"Model saved to: {output_model_path}")
# ===================== EVALUATION =====================
