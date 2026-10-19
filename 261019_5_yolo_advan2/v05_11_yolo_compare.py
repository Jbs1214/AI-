import time
import cv2
from ultralytics import YOLO

# 1. 모델 선택 — 이 줄만 바꿔가며 비교
# model = YOLO("yolo11n.pt")
model = YOLO("yolo11n_openvino_model/")

# 2. 비디오 경로 설정
cap = cv2.VideoCapture("dance.mp4")

# 3. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    start_time = time.perf_counter()    # 추론 시작 시간

    results = model(frame, verbose = False)

    end_time = time.perf_counter()

    if_time = end_time - start_time
    fps = 1 / if_time

    # 3-5 결과 시각화
    annotated_frame = results[0].plot()

    cv2.putText(
        annotated_frame,
        f"FPS: {fps:.1f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )
    # 화면보다 큰 영상은 표시할 때만 높이 720에 맞춰 축소 (추론은 원본 크기)
    h, w = annotated_frame.shape[:2]
    if h > 720:
        annotated_frame = cv2.resize(annotated_frame, (int(w * 720 / h), 720))
    cv2.imshow("compare", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()