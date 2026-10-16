from ultralytics import solutions
import cv2

cap = cv2.VideoCapture("https://cctvsec.ktict.co.kr/6655/XGhHNxKJ+h8VwlAfiIVp0hz7pu3v25OX3GLrr9KtgA3vg/fzy7WDUtKiyhyf4JCj")

# show=False: 창은 라이브러리가 아니라 우리가 직접 관리 (q 종료 시 창 충돌 방지)
distance = solutions.DistanceCalculation(
    model="yolo11n.pt",
    show=False,
    conf=0.4
)

# 창을 먼저 만들고 마우스 클릭 콜백 연결 (왼쪽 클릭: 객체 2개 선택 / 오른쪽 클릭: 선택 해제)
WINDOW = "DISTANCE"
cv2.namedWindow(WINDOW)
cv2.setMouseCallback(WINDOW, distance.mouse_event_for_distance)

# 상태별 색상 (BGR)
COLORS = {
    "SAFE": (0, 200, 0),       # 초록
    "Warning": (0, 165, 255),  # 주황
    "DANGER": (0, 0, 255),     # 빨강
}

# 3. 비디오 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 읽기 실패")
        break

    # 3-1. 거리 계산 수행
    results = distance.process(frame)
    annotated = results.plot_im

    # 3-2. pixels_distance 추출
    pixel_distance = results.pixels_distance

    # 아직 거리 측정 안 됐을 때 (좌클릭 2회로 대상 2개를 고르기 전)
    if not pixel_distance:
        cv2.putText(annotated, "Click 2 objects", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        # 3-3. 거리 조건에 따른 상태 정의
        if pixel_distance >= 150:
            status = "SAFE"
        elif pixel_distance >= 100:
            status = "Warning"
        else:
            status = "DANGER"
        color = COLORS[status]

        # 3-4. 선택한 두 객체의 중심을 상태 색 선으로 다시 그리기 (라이브러리 선 위에 덮어씀)
        centers = []
        for box in distance.selected_boxes.values():
            x0, y0, x1, y1 = distance.get_enclosing_box(box)
            centers.append((int((x0 + x1) / 2), int((y0 + y1) / 2)))
        if len(centers) == 2:
            cv2.line(annotated, centers[0], centers[1], color, 4)
            for c in centers:
                cv2.circle(annotated, c, 6, color, -1)

        # 3-5. 화면에 거리와 상태 표시
        cv2.putText(annotated, f"{int(pixel_distance)}px  {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
        if status == "DANGER":
            cv2.rectangle(annotated, (0, 0), (annotated.shape[1] - 1, annotated.shape[0] - 1), color, 8)

    cv2.imshow(WINDOW, annotated)

    # 3-6. q 키로 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Q 키를 눌러서 종료합니다.")
        break

# 4. 자원 해제
cap.release()
cv2.destroyAllWindows()
