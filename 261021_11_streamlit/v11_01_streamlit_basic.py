import streamlit as st           # 웹앱 만드는 도구 (코드 → 웹화면)
from ultralytics import YOLO     # 사물 찾는 AI 라이브러리
import cv2                        # 영상·이미지 처리 도구 (OpenCV)

# 1. Streamlit 페이지 기본 설정 — 웹 화면 모양 결정
st.set_page_config(layout="wide") # 화면을 가로로 넓게 사용 (꼭 코드 맨 위)
st.title("YOLO 실시간 CCTV 탐지")  # 페이지 맨 위에 큰 제목 표시

# 2. 영상 출력용 공간 설정 — 영상이 들어갈 빈 액자 준비
frame_placeholder = st.empty()    # 사진을 계속 갈아끼울 자리 (placeholder)

# 3. CCTV 비디오 스트림 연결 — 인터넷 CCTV 카메라 접속
cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv013.stream/playlist.m3u8")

# 4. 모델 로드 — 사물 인식 AI 두뇌 불러오기
model = YOLO("yolo11n.pt")        # yolo11n.pt = 이미 학습된 AI 파일

# 5. 비디오 프레임 처리 — CCTV 영상을 한 장씩 분석 반복
while cap.isOpened():             # CCTV 연결되어 있는 동안 계속 반복
    success, frame = cap.read()   # 영상에서 사진 한 장 가져오기
    if not success:               # 사진 못 가져오면
        print("프레임 읽기 실패")
        st.warning("프레임 읽기 실패(Streamlit)")
        break                     # 반복 멈추기

    # 5-1. 모델로 객체 탐지 수행 — AI에게 사진 보여주고 분석 요청
    results = model(frame)

    # 5-2. 탐지 결과를 이미지에 시각화 — 찾은 사물에 네모 박스 그리기
    annotated_frame = results[0].plot()

    # 5-3. Streamlit placeholder에 프레임 갱신 — 빈 액자에 결과 사진 표시
    frame_placeholder.image(annotated_frame, channels="BGR")  # BGR = OpenCV 색 순서

# 6. 자원 해제 — 끝나면 카메라·창 닫기 (메모리 정리)
cap.release()                     # CCTV 연결 끊기
cv2.destroyAllWindows()           # 열린 창 모두 정리