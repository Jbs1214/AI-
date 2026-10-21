from transformers import pipeline

# 1. 감정 분석 파이프라인 생성
# 다국어(한국어 포함) 리뷰 감정 모델 : 결과가 1 star ~ 5 stars 로 나옴
classifier = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
)

# 2. 분석할 문장 입력
# 2-1. 긍정 문장
# text = "오늘 기분이 정말 좋아요"

# 2-2. 부정 문장
# text = "오늘 기분이 정말 별로예요"

# 2-3. 애매한 문장
text = "음식은 정말 훌륭했지만, 직원이 불친절해서 다시는 가고 싶지 않아요."

# 3. 문장 분석
results = classifier(text)

# 4. 별점(1~5) → 감정으로 변환
stars = int(results[0]["label"][0])
if stars >= 4:
    label = "긍정"
elif stars <= 2:
    label = "부정"
else:
    label = "중립"

print(f"문장의 감정 분석 결과 : {label} ({stars}점 / 5점)")
print(f"문장의 감정 분석 점수 : {results[0]['score']:.4f}")
