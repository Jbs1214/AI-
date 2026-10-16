from ultralytics import solutions
import cv2

cap = cv2.VideoCapture("https://cctvsec.ktict.co.kr/6655/XGhHNxKJ+h8VwlAfiIVp0hz7pu3v25OX3GLrr9KtgA3vg/fzy7WDUtKiyhyf4JCj")

# show=False: 창은 라이브러리가 아니라 우리가 직접 관리 (q 종료 시 창 충돌 방지)
distance = solutions.DistanceCalculation(
    model="yolo11n.pt",
    show=False,
    conf = 0.4
)

# 창을 먼저 만들고 마우스 클릭 콜백 연결 (왼쪽 클릭: 객체 2개 선택 / 오른쪽 클릭: 선택 해제)
WINDOW = "DISTANCE"
cv2.namedWindow(WINDOW)
cv2.setMouseCallback(WINDOW, distance.mouse_event_for_distance)

# 3. 프레임 처리 루프
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 읽기 실패")
        break

    results = distance(frame)
    cv2.imshow(WINDOW, results.plot_im)

    # 3-2. q 키로 종료
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("q키를 눌러서 종료!!")
        break

# 4. 자원 해제
cap.release()
cv2.destroyAllWindows()
