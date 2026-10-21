from transformers import pipeline

# 1. 감정 분석 파이프라인 생성
classifier = pipeline("sentiment-analysis")

# 2. 분석할 문장 입력
# 2-1. 긍정 문장
# text = "i'm feeling really great today"

# 2-2. 부정 문장
# text = "i'm feeling really nurvous today"

# 2-3. 애매한 문장
text = "The food was incredible, but I’d never go back because of the rude staff."

# 3. 문장 분석
results = classifier(text)

print(f"문장의 감정 분석 결과 : {results[0]['label']}")
print(f"문장의 감정 분석 점수 : {results[0]['score']:.4f}")
