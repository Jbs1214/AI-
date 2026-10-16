from ultralytics import YOLO
import cv2

# 1. 비디오/스트림 경로 설정
cap = cv2.VideoCapture("https://cctvsec.ktict.co.kr/6641/NLj3WMlKeAg0m2vy7BJTagJkiKPG163gCyrTIY+2l71oIbbhXf3wEmpkoADrJOHQ")

# 2. 모델 로드
model = YOLO("yolo11n.pt")

while cap.isOpened() :
    success, frame = cap.read()

    if not success :
        print("프레임 확인")
        break

    results = model.track(frame, persist=True, conf=0.4)

    annotated_frame = results[0].plot()

    window_name = "CCTV_YOLO_TRACK"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow("CCTV_YOLO_TRACK", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q를 눌러서 종료하세요")
        break

cap.release()
cv2.destroyAllWindows()