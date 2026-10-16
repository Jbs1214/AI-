import os
from pathlib import Path
from ultralytics import solutions
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import cv2


class MyAlarm(solutions.SecurityAlarm):
    subject = "현재 경고임"          # 메일 제목
    image_name = "탐지 경고.jpg"     # 첨부 이미지 이름

    def send_email(self, im0, records=5):
        img_bytes = cv2.imencode(".jpg", im0)[1].tobytes()

        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = self.to_email
        message["Subject"] = self.subject
        message.attach(MIMEText(f"Ultralytics alert: {records} object(s) detected."))
        message.attach(MIMEImage(img_bytes, name=self.image_name))

        try:
            self.server.send_message(message)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")


stream_url = "http://210.99.70.120:1935/live/cctv009.stream/playlist.m3u8"
cap = cv2.VideoCapture(stream_url)
assert cap.isOpened(), "스트림 열기 실패 — 경로/네트워크 확인"

# 메일 계정 정보는 프로젝트 루트의 .env 파일에서 읽음 (.env는 git에 올라가지 않음)
env_path = Path(__file__).resolve().parent.parent / ".env"
for line in env_path.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

from_email = os.environ["MAIL_FROM"]
password = os.environ["MAIL_APP_PASSWORD"]
to_email = os.environ["MAIL_TO"]

# 3. 모델 로드 및 알람 객체 생성
google_alarm = MyAlarm(
    model="yolo11n.pt",
    show=False,
    records=2,      # 한 프레임에 N개 이상 탐지되면 메일 1회 (기본 5)
    classes=[2],   # 탐지 대상 클래스 (2 = 자동차)
)

# 4. SMTP 서버 인증 (1회만 실행 → 세션 유지)
google_alarm.authenticate(from_email, password, to_email)

# 5. 비디오 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("스트림 읽기 실패 . . .")
        break

    # 탐지 → 추적 → 임계치 도달 시 메일 발송 (내부 자동 처리)
    results = google_alarm(frame)

    # 처리된 프레임 표시 (show=False → 우리가 직접 창을 띄움)
    cv2.imshow("SECURITY ALARM", results.plot_im)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q키를 눌러서 종료")
        break

# 6. 자원 해제
cap.release()
cv2.destroyAllWindows()