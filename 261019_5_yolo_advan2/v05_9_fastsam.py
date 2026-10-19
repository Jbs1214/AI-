from ultralytics import SAM, FastSAM
import cv2

# 1. 이미지 경로
source = "261019_5_yolo_advan2/cat.jpg"

# 2. 모델 로드
model = FastSAM("FastSAM-s.pt")

# 3. 모델 추론
results = model(source, texts = "cat")

# 4. 결과 이미지 가져오기
output_path = "./output_result.jpg"
output_image = results[0].plot()

# 5. 결과 이미지 저장
cv2.imwrite(output_path, output_image)

print("코드 실행 완료")

print("코드 실행 완료")

