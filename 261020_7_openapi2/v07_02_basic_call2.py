from groq import Groq
from dotenv import load_dotenv
import os

# 1. .env의 API키를 환경변수로 불러옴
load_dotenv()

# 2. 키로 클라이언트 만들기
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 3. 질문 보내기
answer = input("질문을 입력해주세요 : ")
res = client.chat.completions.create(
    model="openai/gpt-oss-20b",  # 무료, 빠름 / oss : open-source-software / 20은 모델 파라미터 수(20억개)
    messages=[
        {
            "role": "user",  # 질문이나 요청할때
            "content": answer,  # 질문
        }
    ],
)

# 4. 답변 받기
result = res.choices[0].message.content
print(result)