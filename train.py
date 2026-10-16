# 1. 라이브러리 불러오기
from ultralytics import YOLO

# 2. 모델 로드 (분류 전용 pretrained: yolo11n-cls.pt)
model = YOLO("yolo11n-cls.pt")

# 3. 모델 학습
model.train(
    data = "./dataset", 
    epochs = 30,
    imgsz = 256,
    patience = 10
)