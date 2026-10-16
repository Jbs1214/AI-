from ultralytics import YOLO
import cv2

# 1. 모델 로드
model = YOLO("yolo11n-cls.pt")
# n -> s -> m -> l -> x

# 2. 모델 추론
results = model("261014_2_yolo_basic/cat.jpg")

# 3. 결과 시각화
result_image = results[0].plot()

# 4. 결과 이미지 저장
output_result_img_path = "./output.jpg"
cv2.imwrite(output_result_img_path, result_image)
# 5. 