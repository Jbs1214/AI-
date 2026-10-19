from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")
stream_url = "https://cctvsec.ktict.co.kr/6641/NLj3WMlKeAg0m2vy7BJTatlNcGfRQLm6kYzzxEpsD9m6zUu1AWgYh1p3Hl0Hry8A"
cap = cv2.VideoCapture(stream_url)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("CCTV URL 또는 웹캠 확인해주세요.")
        break

    result = model(frame, conf=0.5)
    annotated_frame = result[0].plot()

    cv2.imshow("CCTV YOLO", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q를 눌러서 종료")
        break

cap.release()
cv2.destroyAllWindows()