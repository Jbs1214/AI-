from transformers import pipeline

# 1. 텍스트 생성 파이프라인 생성
generator = pipeline("text-generation", model="gpt2")

# 2. 시드 문장 입력 (이어 쓸 첫 부분)
q = input("이어서 쓸 첫 문장을 입력해주세요 : ")

# 3. 텍스트 생성 실행
results = generator(
    q,
    max_new_tokens=50,
    num_return_sequences=1,
)

# 4. 결과 출력
print(results[0]["generated_text"])