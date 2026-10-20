from dotenv import load_dotenv
import os
from groq import Groq

# 환경 변수 불러오기
load_dotenv()

# API 입력
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# 대화 기록 맨 앞에 AI 성격 및 규칙 지정
messages = [
    {
        "role": "system",
        "content": "너는 곰돌이 푸야 근데 개발을 아주 잘 알고 있어. 반말해도 돼",
    }
]

# 질문 입력
while True:
    q = input("(종료하려면 'q'를 입력해줘!) 나 :")
    if q == "q":
        print("또 봐!")
        break

    messages.append({"role": "user", "content": q})

    res = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.1,  # 낮을수록 일관된 답
        max_completion_tokens=300,  # 답변 최대 길이
        reasoning_effort="low",
    )

    # 답변 받기
    answer = res.choices[0].message.content

    from termcolor import colored

    color_answer = colored(answer, "yellow")
    print("푸:", color_answer)

    messages.append({"role": "assistant", "content": answer})

