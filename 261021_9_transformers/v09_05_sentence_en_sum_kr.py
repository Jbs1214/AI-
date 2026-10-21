from transformers import pipeline
from deep_translator import MyMemoryTranslator

# 1. 요약 파이프라인
summerizer = pipeline("summarization", model="t5-small")

# 2. 요약할 문장
text = """
NOTICE REGARDING THE TEMPORARY RELOCATION OF THE MONTHLY STAFF GATHERING

We would like to take this opportunity to inform all members of staff, regardless of department, seniority, or length of service, that following extensive internal discussions and careful consideration of a number of practical factors, including but not limited to scheduling conflicts, the availability of suitable space, and the ongoing renovation work currently taking place on the third floor, it has been decided that the monthly staff gathering, which would ordinarily be held in the third-floor conference hall on the last Friday of each month, will, for the month of November only, be held instead in the ground-floor cafeteria at 3:00 p.m.

Staff members are kindly reminded that this change applies solely to the upcoming November gathering. Beginning in December, once the renovation work has been completed, the gathering will return to its usual location and time, and no further changes are anticipated at this stage. Those who are unable to attend are asked to inform their team leaders in advance, although no formal documentation is required.

We apologize for any inconvenience this temporary arrangement may cause and thank everyone in advance for their understanding and cooperation.spective of whether any particular User has actually read it.
"""

# 3. 요약 실행
summary = summerizer(
    text,
    min_length=20,  # 최소 토큰
    max_length=500,  # 최대 토큰
    do_sample=False,  # 매번 동일 결과 출력
)

# 4. 결과 확인 (번역은 모델 없이 MyMemory 웹 서비스 사용)
sum_text = summary[0]["summary_text"]
kr_text = MyMemoryTranslator(source="en-US", target="ko-KR").translate(sum_text)
print(f"요약된 결과 : {sum_text}")
print(f"한국어 번역 : {kr_text}")