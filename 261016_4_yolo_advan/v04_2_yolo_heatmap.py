from ultralytics import solutions
import cv2

cap = cv2.VideoCapture(0)

heatmap = solutions.Heatmap(
    model = "yolo11n.pt",
    show = False,
    colormap=cv2.COLORMAP_COOL
)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("비디오 읽기 실패 . . .")
        break

    results = heatmap(frame)

    cv2.namedWindow("HEATMAP", cv2.WINDOW_NORMAL)
    cv2.imshow("HEATMAP", results.plot_im)
    if cv2.waitKey(1) & 0xFF == ord('q'):
            print("q키를 눌러서 종료")
            break

cap.release()
cv2.destroyAllWindows()
