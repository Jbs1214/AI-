from ultralytics import solutions

# 1. 검색 앱 생성 — CPU에서 동작 (GPU면 "cuda")
app = solutions.SearchApp(
    data="images/etc",  # 사진이 바로 들어있는 폴더 (하위 폴더는 검색 안 함)
    device="cpu"
)

# 2. 웹 서버 실행 → 브라우저에서 http://127.0.0.1:5000 접속
app.run(debug=True)   # 개발용 / 운영 시 False