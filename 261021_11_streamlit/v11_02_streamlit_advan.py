import streamlit as st             # 웹앱 도구
from ultralytics import YOLO       # 사물 찾는 AI
import cv2                          # 영상 처리 도구
import pandas as pd                 # 표(엑셀 같은) 만드는 도구
import plotly.express as px         # 그래프 그리는 도구 (pip install plotly)
import time                         # 시간 측정용

# 1. 화면 구성 — 화면을 좌·우 2칸으로 분할
# 좌/우 2개 컬럼 생성
col1, col2 = st.columns(2)         # 같은 너비 두 칸 만들기

with col1:                          # 왼쪽 칸에는
    frame_placeholder = st.empty() # 왼쪽 컬럼 : YOLO 프레임 표시용 빈 영역

with col2:                          # 오른쪽 칸에는
    chart_placeholder = st.empty() # 오른쪽 컬럼 : 객체 수 그래프 표시용 빈 영역

# 2. 비디오 경로 설정 — CCTV 주소 연결
cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv013.stream/playlist.m3u8")

# 3. 모델 로드 — AI 두뇌 불러오기 (캐시로 1회만 로드)
@st.cache_resource           # 모델·DB 같은 무거운 자원 캐싱 (재실행해도 1번만 로드)
def load_model():
    return YOLO("yolo11n.pt")    # 캐시 안 쓰면 화면 조작으로 스크립트가 재실행될 때마다 모델 새로 읽음 → 느림

model = load_model()              # 두 번째 호출부터는 캐시에서 즉시 반환

# 4. 비디오 프레임 처리 — 영상 한 장씩 분석 + 그래프 동시 갱신
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        st.warning("CCTV FRAME ERROR")
        break

    # 4-1. YOLO 모델 객체 탐지 수행 — AI한테 사진 보여주기
    results = model(frame)

    # 4-2. 탐지 결과가 그려진 프레임 이미지 생성 — 네모 박스 그리기
    annoated_frame = results[0].plot()

    # 4-3. 탐지된 객체의 클래스 이름 추출 — "사람"·"차" 이름 모으기
    labels = [model.names[int(c)] for c in results[0].boxes.cls]

    # 4-4. 탐지 객체 수 시각화 — 종류별 개수 세서 막대 그래프 만들기
    if labels:                      # 뭔가 찾았으면
        # labels 리스트를 DataFrame으로 변환 후 객체별 개수 집계
        df_count = pd.DataFrame({"Object" : labels})
        df_count = df_count.value_counts().reset_index(name="Count")  # 종류별 개수 세기

        # Plotly를 이용해 막대 그래프 생성
        fig = px.bar(
            df_count,
            x="Object",             # 가로축 = 사물 이름
            y="Count",              # 세로축 = 개수
            title="탐지 객체 수",
            color="Object",         # 사물마다 색 다르게
            text="Count"            # 막대 위에 숫자 표시
        )
    else:                           # 아무것도 못 찾았으면
        df_count = pd.DataFrame({"Object": [], "Count": []})           # 빈 표 만들기
        fig = px.bar(
            df_count,
            x="Object",
            y="Count",
            title="탐지 객체 수"
        )

    # 4-5. Streamlit에 결과 표시 — 왼쪽 영상 + 오른쪽 그래프 동시 갱신
    frame_placeholder.image(annoated_frame, channels="BGR")
    chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")
    # key=f"chart_{time.time()}" — 매번 다른 이름 줘서 위젯 충돌 막기

# 5. 자원해제 — CCTV 연결 끊고 창 닫기
cap.release()
cv2.destroyAllWindows()