import cv2
import numpy as np

# Load MiDaS small (fast for RTX 3050)
model_type = "MiDaS_small"

midas = cv2.dnn.readNet("midas_small.onnx")  # download once

def estimate_depth(frame):
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (256, 256), swapRB=True, crop=False)
    midas.setInput(blob)
    depth = midas.forward()

    depth = depth[0, :, :]
    depth = cv2.resize(depth, (frame.shape[1], frame.shape[0]))

    return depth

def get_depth_at(depth_map, x, y):
    h, w = depth_map.shape
    x = min(max(x, 0), w-1)
    y = min(max(y, 0), h-1)

    return float(depth_map[y, x])