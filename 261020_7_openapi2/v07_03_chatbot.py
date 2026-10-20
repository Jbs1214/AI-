from dotenv import load_dotenv
from groq import Groq
import os

# 환경 변수 불러오기
load_dotenv()

# 클라이언트 만들기 (GROQ API 요청)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 대화 기록
messages = []

# 'exit' 입력 전까지 반복
while True:
    q = input("(종료하시려면 'exit'를 입력하세요.) 나 : ")
    if q == "exit":
        print("대화를 종료합니다.")
        break

    messages.append({"role": "user", "content": q})
    res = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
    )
    answer = res.choices[0].message.content

    from termcolor import colored

    color_answer = colored(answer, "red")
    print("AI:", color_answer)

    # AI 답도 기록에 추가 → 다음 질문 때 앞 대화를 앎
    messages.append({"role": "assistant", "content": "answer"})
