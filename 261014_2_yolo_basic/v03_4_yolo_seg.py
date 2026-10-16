from ultralytics import YOLO
import cv2

model = YOLO("yolo11n-seg.pt")

result = model("./pose.jpg", save = True)

