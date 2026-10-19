import cv2

# 1. 비디오 경로 설정
cap = cv2.VideoCapture("https://cctvsec.ktict.co.kr/6570/slzNyfjZScqUil9yWzqaoStNALY/QlwpRHO0JmQTVtDC1fp/aPayBezJmmfqoVj5")

# 2. 마우스 이벤트 처리 함수 정의
points = []
def mouse_callback(event, x, y, flags, param):
    """
    마우스 클릭해서 x, y 좌표 가져오기
    """
    if event == cv2.EVENT_LBUTTONDOWN :
        points.append((x, y))
        print(f"클릭된 좌표 : {x, y}")

# 3. 윈도우 창 설정 및 함수 등록
cv2.namedWindow("GET_X_Y", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("GET_X_Y", mouse_callback)

# 4. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success :
        print("프레임 확인해주세요")
        break

    re_frame = cv2.resize(frame, (640, 480))

    cv2.imshow("GET_X_Y", re_frame)

    if cv2.waitKey(100) & 0xFF == ord('q'):
        print("q 키를 눌러서 종료합니다.")
        break

# 5. 자원 해제
cap.release()
cv2.destroyAllWindows()

# 6. 좌표 사용 안내
# 1번 : 좌상단
# 2번 : 좌하단
# 3번 : 우하단
# 4번 : 우상단