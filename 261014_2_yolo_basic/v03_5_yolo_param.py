from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")

result = model("./safari.jpg", save = True, conf=0.2, save_crop = True, save_txt=True)

