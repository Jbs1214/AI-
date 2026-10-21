from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient

load_dotenv()  # .env 의 HF_TOKEN 불러오기
client = InferenceClient(provider="auto", api_key=os.getenv("HF_TOKEN"))

# 1단계 → 이미지 설명 입력
answer = input("생성할 이미지를 설명해주세요. : ")

# 2단계 → 왜: 텍스트는 픽셀 아님, 모델이 의미 해석 후 픽셀 합성 필요
#         어떻게: text_to_image() 호출 → PIL.Image 객체 반환
image = client.text_to_image(
    answer,
    model="black-forest-labs/FLUX.1-dev",
)

# 3단계 → PIL.Image.save() 호출, 확장자로 포맷 자동 결정
image.save("tti_result.jpg")

print("전체 코드가 잘 실행됐습니다.")