from transformers import AutoTokenizer, pipeline

# 1. 한국어 전용 GPT 모델(polyglot-ko) 텍스트 생성 파이프라인 생성
model_name = "EleutherAI/polyglot-ko-1.3b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
# 이 모델은 token_type_ids 를 받지 않으므로 입력에서 제외
tokenizer.model_input_names = ["input_ids", "attention_mask"]

generator = pipeline(
    "text-generation",
    model=model_name,
    tokenizer=tokenizer,
)

# 2. 시드 문장 입력 (이어 쓸 첫 부분)
q = input("이어서 쓸 첫 문장을 입력해주세요 : ")

# 3. 텍스트 생성 실행
results = generator(
    q,
    max_new_tokens=50,
    num_return_sequences=1,
    do_sample=True,  # 확률적으로 단어 선택
    temperature=0.7,  # 낮을수록 안정적, 높을수록 다양
    top_p=0.9,  # 누적 확률 90% 안의 후보만 사용
    repetition_penalty=1.2,  # 같은 말 반복 억제
    pad_token_id=tokenizer.eos_token_id,
)

# 4. 결과 출력
print(results[0]["generated_text"])
