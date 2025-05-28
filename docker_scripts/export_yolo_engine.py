
from ultralytics import YOLO
import os
import shutil

MODEL_SAVE_DIR = "/app/cv4gt_repo/models"

# --- Define the specific .pt model you want to convert ---
SOURCE_PT_MODEL = "YOLOv8s-cv4gt-data-20-05_239e.pt"
SOURCE_PT_PATH = os.path.join(MODEL_SAVE_DIR, SOURCE_PT_MODEL)

ENGINE_NAME = os.path.splitext(SOURCE_PT_MODEL)[0] + ".engine"


print(f"Loading PyTorch model from {SOURCE_PT_PATH}...")
model = YOLO(SOURCE_PT_PATH)

print(f"Exporting {SOURCE_PT_MODEL} to TensorRT engine...")
model.export(format="engine", half=True, opset=13, imgsz=640, name=ENGINE_NAME)

print("TensorRT engine export and placement complete.")