from ultralytics import YOLO

model = YOLO("yolo11n.pt")
model("./input_want.jpg", classes=[55], save=True)   # 55 = cake (COCO)