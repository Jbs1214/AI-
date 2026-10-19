import urllib.request
import json
import pandas as pd
from ultralytics import YOLO
import cv2                  

def its_cctv(cctv_index):

    # 1. 인증 키
    key = "db5c00dc1fce45c49049bff225a0fea6"
    # 과금 우려 있는 API KEY는 .env 환경변수로 관리

    # 2. 도로 유형(its = 일반도로, ex = 고속도로) -> 어느 도로 CCTV 타입 정하기
    road_type = "its"

    # 3. 관심 영역 (경도·위도 범위) → 지도 위에 사각형 그려서 그 안 CCTV만 요청
    minX, maxX = 120.95, 127.02   # 동서(가로) 범위 → 한국 전체 가로
    minY, maxY = 30.55, 37.69     # 남북(세로) 범위 → 한국 전체 세로
    getType = "json"              # 응답 형식 → JSON(글자로 정리된 자료)

    # 4. API URL 조립 → 위 정보를 모두 합쳐서 "자료 요청 주소" 한 줄로 만듦
    url_cctv = (
        f"https://openapi.its.go.kr:9443/cctvInfo"
        f"?apiKey={key}&type={road_type}&cctvType=1"
        f"&minX={minX}&maxX={maxX}"
        f"&minY={minY}&maxY={maxY}&getType={getType}"
    )
    # 5. 요청
    response = urllib.request.urlopen(url_cctv)

    # 6. bytes -> str
    json_str = response.read().decode("utf-8")
    # print(json_str)
    json_dict = json.loads(json_str)    # str -> dict(사전 모양)
    # print(json_dict)

    # 7. 데이터 프레임 변환
    cctv_play = pd.json_normalize(
        json_dict["response"]["data"] ,sep=''
        )

    # print(cctv_play)
    # 8. CCTV URL 출력
    cctv_url = cctv_play['cctvurl'][cctv_index]
    # print(cctv_url)

    return cctv_url

if __name__ == "__main__":  # 직접 실행할 때만 동작 (import 시에는 실행 안 됨)
    cap = cv2.VideoCapture(its_cctv(4))   # 함수를 호출해서 나온 URL(str)을 넘김

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