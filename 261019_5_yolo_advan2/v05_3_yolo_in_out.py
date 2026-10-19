from ultralytics import solutions
import cv2

cap = cv2.VideoCapture("https://cctvsec.ktict.co.kr/6570/slzNyfjZScqUil9yWzqaoStNALY/QlwpRHO0JmQTVtDC1fp/aPayBezJmmfqoVj5")

# 2. 카운팅 선 설정 (2점 — 시작점 → 끝점)
count_points = [(234, 407), (620, 340)]   # 좌하 → 우상 사선

# 3. 모델 로드 및 카운터 객체 생성
counter = solutions.ObjectCounter(
    model="yolo11n.pt",        # YOLO11 nano 모델 — 속도 우선
    show=False,                 # 솔루션 내부 창 끔 (직접 imshow로 표시)
    region=count_points         # 2점 리스트 → 가상 선 (4점 주면 다각형 영역으로 카운트)
)

# 4. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 읽기 실패")
        break

    # 4-1. 프레임 리사이즈 (선 좌표계와 일치 필수)
    re_frame = cv2.resize(frame, (640, 480))

    # 4-2. 탐지 + 트래킹 + 선 통과 판정 + IN/OUT 카운트 (한 줄에서 모두 처리)
    results = counter(re_frame)

    # 4-3. 처리된 프레임 표시 (show=False → 우리가 직접 창을 띄움)
    cv2.imshow("IN/OUT COUNT", results.plot_im)

    # 4-4. q 키로 종료
    # waitKey가 없으면 창이 갱신되지 않아 '응답 없음'이 되고 q로 끌 수도 없음
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Q 키를 눌러서 종료")
        break

# 5. 자원 해제
cap.release()
cv2.destroyAllWindows()    # imshow로 연 창 정리