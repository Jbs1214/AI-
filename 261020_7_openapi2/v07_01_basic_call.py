from groq import Groq
from dotenv import load_dotenv
import os

# 1. .env의 API키를 환경변수로 불러옴
load_dotenv()

# 2. 키로 클라이언트 만들기
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 3. 질문 보내기
res = client.chat.completions.create(
    model="openai/gpt-oss-20b",  # 무료, 빠름 / oss : open-source-software / 20은 모델 파라미터 수(20억개)
    messages=[
        {
            "role": "user",  # 질문이나 요청할때
            "content": "지구 온난화 진행도 얼마인지와 향후 몇년 뒤에 심각하게 위험할지, 어떻게 지구가 변화할지 설명",  # 질문
        }
    ],
)

# 4. 답변 받기
result = res.choices[0].message.content
print(result)