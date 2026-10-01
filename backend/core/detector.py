from ultralytics import YOLO
import torch
from app.config import *

class Detector:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        print(f"🚀 YOLO running on {self.device.upper()}")

        # Warmup (IMPORTANT for smooth FPS)
        self.model.predict(
            source=torch.zeros(1, 3, 320, 320).to(self.device),
            imgsz=320,
            verbose=False
        )