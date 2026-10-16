from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")

stream_url = "https://cctvsec.ktict.co.kr/6655/XGhHNxKJ+h8VwlAfiIVp0nciMXM2os3M1NRLI8S9v1sbB+6HxW0HGtj2+2CG47ot"

cap = cv2.VideoCapture(stream_url)

while cap.isOpened() :
    success, frame = cap.read()

    if not success :
        print("웹캠을 불러오지 못했습니다.")
        break

    results = model(frame, conf=0.5)
    annotated_frame = results[0].plot()

    count = len(results[0].boxes)
    status = "Safe"
    color = (255, 0, 0)

    cv2.putText(
        annotated_frame,

        f"Detected : {count}, {status}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        color,
        2,
        cv2.LINE_AA
    )

    cv2.imshow("CCTV detection", annotated_frame)

    # 3-8. q 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('q 키를 눌러서 종료합니다.')
        break

cap.release()
cv2.destroyAllWindows()