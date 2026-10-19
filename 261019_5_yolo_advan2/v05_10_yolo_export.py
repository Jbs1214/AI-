from ultralytics import YOLO

# 1. 원본 PyTorch 모델 로드
model = YOLO("yolo11n.pt")

# 2. OpenVINO 형식으로 변환 (= CPU 부스터 장착)
model.export(format="openvino")
# 결과: yolo11n_openvino_model/ 폴더 자동 생성