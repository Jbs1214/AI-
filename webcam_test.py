"""웹캠으로 표정 분류 모델을 직접 테스트한다. 종료: q 키.

실행: python webcam_test.py  (dataset 폴더와 같은 위치에서)
"""
import cv2
from ultralytics import YOLO

model = YOLO("runs/classify/train-3/weights/best.pt")  # 사용할 가중치 경로

cap = cv2.VideoCapture(0)  # 0 = 기본 웹캠

while cap.isOpened():
    ok, frame = cap.read()
    if not ok:
        break

    result = model(frame, imgsz=256, verbose=False)[0]
    label = result.names[result.probs.top1]
    conf = float(result.probs.top1conf)

    cv2.putText(frame, f"{label} {conf:.2f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("webcam", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
