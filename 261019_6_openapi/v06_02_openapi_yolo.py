import urllib.request
import json
import pandas as pd
from ultralytics import YOLO
import cv2
from v06_03_openapi_def import its_cctv   # 같은 폴더의 파일에서 함수 가져오기

cctv_url = its_cctv(4)   # 5번째 CCTV의 영상 주소
cap = cv2.VideoCapture(cctv_url)

model = YOLO("yolo11n.pt")

# 3. 프레임 처리 루프
while cap.isOpened():
    success, frame = cap.read()                # 한 프레임 읽기
    if not success:
        print("프레임 읽기 실패")
        break

    results = model(frame)
    annotated_frame = results[0].plot()

    cv2.namedWindow("OPENAPI", cv2.WINDOW_NORMAL)
    cv2.imshow("OPENAPI", annotated_frame)

    # 3-3. q 키 입력 시 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q 키를 눌러서 종료합니다.")
        break

# 4. 자원 해제
cap.release()
cv2.destroyAllWindows()