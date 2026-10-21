from sentence_transformers import SentenceTransformer, util

# 1. 모델 로드
model = SentenceTransformer("jhgan/ko-sroberta-multitask")
"""
jhgan/ko-sroberta-multitask 모델 설명
 - 한국어 문장 데이터(KorSTS, KorNLI)로 학습된 RoBERTa 기반 문장 임베딩 모델, 768차원 벡터 출력
 - 한국어 문장을 의미 공간에 매핑 (방향이 곧 의미)
 - 특징
   1. 한국어 의미 유사도에 특화 (글자가 달라도 뜻이 같으면 높은 유사도)
   2. 검색·추천·중복 탐지·클러스터링에 사용
"""

# 3. 비교할 두 문장 정의
# 의미상 완전히 같은 문장 예시 → 높은 유사도 기대
sen1 = "나는 사과를 좋아해"
sen2 = "난 과일 중에 애플이 최고야"

# 4. 문장 → 숫자 좌표로 바꾸기 (인코딩)
# (쉽게) 문장 한 개를 숫자 768개로 표현 → 의미가 비슷하면 숫자 묶음도 비슷한 모양
# 컴퓨터는 글자보다 숫자를 잘 이해 → 비교·계산하려면 먼저 숫자로 변환 필수

emb1 = model.encode(
    sen1, convert_to_tensor=True
)  # 결과를 Tensor(파이토치 숫자 상자)로 받기
emb2 = model.encode(sen2, convert_to_tensor=True)

# 5. 두 좌표가 얼마나 같은 방향인지 측정 (코사인 유사도)
# (쉽게) 두 화살표 사이 각도만 봄 → 0도면 1(똑같음), 90도면 0(무관), 180도면 -1(반대)
# 화살표 길이는 무시, 방향만 비교 → 문장 길이 영향 없음

cos_sim = util.pytorch_cos_sim(emb1, emb2)
# 값 범위 해석
#  -1 : 완전히 반대 의미
#   0 : 의미 무관
#   1 : 완전히 동일 의미
# 6. 결과 출력

# .item() → 0차원 Tensor를 파이썬 float 으로 변환 → f-string 포매팅 가능
print(f"두 문장의 유사도 : {cos_sim.item():.4f}")  # 예) 두 문장의 유사도 : 0.9421
