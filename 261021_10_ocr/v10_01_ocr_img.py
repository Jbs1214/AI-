import pytesseract
from PIL import Image
import os

# 1. tesseract 실행 파일 경로 지정
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

# 2. 이미지 불러오기
image = Image.open("261021_10_ocr/mix.jpg")

# 3. OCR 수행
results = pytesseract.image_to_string(
    image,
    lang="eng+kor",
)

# 4. 결과 출력
# print(f"OCR 실행 결과 : {results}")

import easyocr

# 1. EasyOCR 리더 생성 (한국어 + 영어)
# gpu=False → CPU 사용 / GPU 사용 가능하면 True (기본값)
reader = easyocr.Reader(["ko", "en"], gpu=False)

# 2. OCR 수행 (이미지 한 장에서 글자 위치를 찾고 → 읽기)
image_path = "261021_10_ocr/car.jpg"
results = reader.readtext(image_path)

# 3. 결과 출력 : (글자 상자 좌표, 인식한 글자, 신뢰도)
for box, text, conf in results:
    print(f"글자 : {text} / 신뢰도 : {conf:.4f}")

# 4. 인식한 글자만 이어서 출력
print(f"OCR 실행 결과 : {' '.join(r[1] for r in results)}")
"""
OCR 실행 결과 : This is a lot of 12 point text to test the
ocr code and see if it works on all types
of file format.

The quick brown dog jumped over the
lazy fox. The quick brown dog jumped
over the lazy fox. The quick brown dog
jumped over the lazy fox. The quick
brown dog jumped over the lazy fox.
"""
"""
OCR 실행 결과(한글) : Ｌ스트스때스56<1때

이수진

팀장 / 제품개발팀

+123-456-7890
1『6110@「62117/8「620[5166.0007
123 40616 56, 407 다, 51 12345
"""
"""(easyocr)
글자 : 157고 4895 / 신뢰도 : 0.6371
글자 : Nri udes |Jttyl / 신뢰도 : 0.0760
글자 : (Iullulne / 신뢰도 : 0.1020
글자 : 7MOrO3GS리a / 신뢰도 : 0.0075
글자 : TVe / 신뢰도 : 0.3758
글자 : 1s / 신뢰도 : 0.0439
OCR 실행 결과 : 157고 4895 Nri udes |Jttyl (Iullulne 7MOrO3GS리a TVe 1s
"""