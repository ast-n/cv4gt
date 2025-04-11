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


# ===================== SETUP =====================

def test_gps_tag():
    test_image = Image.open("data/test.jpg")

    saved = store.tag_and_store(test_image)

    check_image = Image.open(saved)
    print(check_image.getexif())

# ===================== TRAIN =====================

def train_save_model():
    # Define dataset path | replace folder name with whatever dataset iteration
    DATASET_PATH = "data/training/cv4gt-data-11-04/data.yaml"
    # Define Epochs
    EPOCHS = 10

    print("Working directory:", os.getcwd())
    print("Expected dataset path:", os.path.abspath(DATASET_PATH))


    # YOLO command
    command = f"yolo task=detect mode=train model=yolov8x data={DATASET_PATH} epochs={EPOCHS} imgsz=640"
    os.system(command)

    # Define paths | replace 'train' with whatever iteration
    source_best_model = "runs/detect/train/weights/best.pt"
    target_dir = "models"
    dataset_folder = os.path.basename(os.path.dirname(DATASET_PATH))
    target_model_path = os.path.join(target_dir, f"YOLOv8-{dataset_folder}_{EPOCHS}e.pt")

    # Ensure target exists
    os.makedirs(target_dir, exist_ok=True)

    # Move and rename best.pt
    if os.path.exists(source_best_model):
        shutil.move(source_best_model, target_model_path)
        print(f"Moved and renamed best.pt to: {target_model_path}")
    else:
        print(f"Could not find best.pt at {source_best_model}")




# ===================== EVALUATION =====================


#test_gps_tag()
train_save_model()
