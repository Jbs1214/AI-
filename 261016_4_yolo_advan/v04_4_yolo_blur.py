from ultralytics import solutions
import cv2

# 1. 비디오 경로 설정 (0 = 웹캠, 파일 경로·RTSP도 가능)
cap = cv2.VideoCapture(0)

blurrer = solutions.ObjectBlurrer(
    model = "yolo11n.pt",
    show=False,
    blur_ratio = 0.3
)

# 3. 비디오 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("웹캠 읽기 실패")
        break

    results = blurrer(frame)

    cv2.imshow("BLUR", results.plot_im)

# 3-3. q 키로 종료
    # waitKey가 없으면 창이 갱신되지 않아 '응답 없음'이 되고 q로 끌 수도 없음
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q키를 눌러서 종료")
        break

# 4. 자원 해제
cap.release()
cv2.destroyAllWindows()    # imshow로 연 창 정리