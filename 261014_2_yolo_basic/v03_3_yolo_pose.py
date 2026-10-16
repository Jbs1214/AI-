from ultralytics import YOLO
import cv2

model = YOLO("yolo11n-pose.pt")

result = model("./dance.mp4", save = True)

