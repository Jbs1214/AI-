from ultralytics import solutions
import cv2

# 1. 비디오 경로 설정
cap = cv2.VideoCapture("https://cctvsec.ktict.co.kr/6570/slzNyfjZScqUil9yWzqaoStNALY/QlwpRHO0JmQTVtDC1fp/aPayBezJmmfqoVj5")

# 2. 영역 좌표 설정
region_points = {
    "region1" : [(315, 163),
(287, 252),
(330, 363),
(463, 371),
(496, 265),
(465, 177)],
    "region2" : [(187, 245),
    (120, 370),
    (188, 428),
    (273, 288)]
}

# 클릭된 좌표 : (315, 163)
# 클릭된 좌표 : (287, 252)
# 클릭된 좌표 : (330, 363)
# 클릭된 좌표 : (463, 371)
# 클릭된 좌표 : (496, 265)
# 클릭된 좌표 : (465, 177)

# 3. 모델 로드
yolo_region = solutions.RegionCounter(
    model = "yolo11m.pt",
    conf = 0.2,
    classes = [2, 5, 7],  # car, bus, truck
    show=False,
    region = region_points
) 

# 4. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 확인 바람")
        break

    # 4-1 프레임 크기 조정(좌표계 통일)
    re_frame = cv2.resize(frame, (640, 480))
    
    # 4-2 구역 내 객체 수 계산
    results = yolo_region(re_frame)
    annotated_re_frame = results.plot_im

    # 4-2-1 영역별 객체 수를 화면에 표시
    for i, (name, count) in enumerate(results.region_counts.items()):
        cv2.putText(annotated_re_frame, f"{name}: {count} cars", (10, 30 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # 4-3 처리된 프레임 표시 (show=False -> 직접 창을 띄움)
    cv2.imshow("REGION", annotated_re_frame)

    # 4-4 q 키를 눌러서 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q키를 눌러서 종료합니다.")
        break

# 5. 자원 해제
cap.release()
cv2.destroyAllWindows()