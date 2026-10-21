# 기업 분석 비서

Hugging Face 모델을 활용한 기업 분석 RPA

기업명만 입력하면 주가·재무 지표·최신 뉴스를 자동으로 모으고, Hugging Face의 AI 모델이 분석 리포트로 정리해 줍니다.
웹 화면(Streamlit)과 터미널 두 가지로 실행할 수 있고, 리포트 저장·메일 발송·매일 자동 실행까지 지원합니다.

> 분석 결과는 AI가 공개 데이터를 요약한 참고 자료이며 투자 권유가 아닙니다.

## 하는 일

1. **수집**: 주가·재무 지표(`yfinance`)와 최신 뉴스(구글 뉴스 RSS)를 자동으로 가져옵니다. 별도 키가 필요 없습니다.
2. **분석**: Hugging Face 모델(기본 `deepseek-ai/DeepSeek-V4.1-Flash`)이 한 줄 요약, 긍정·위험 요인, 지켜볼 점을 **짧은 문구**로 정리하고, 뉴스마다 긍정·중립·부정을 판정합니다.
3. **함께 볼 만한 종목**: 같은 업종 기업들의 최근 주가 흐름을 비교해서 보여줍니다. 매수·매도 의견은 내지 않고 사실과 비교만 제공합니다.
4. **오늘의 관심 종목**: 등록된 85개 기업을 주가 흐름만으로 선별해 `최근 3개월 상승률 상위`와 `52주 고점 대비 하락 폭이 큰 기업`을 보여줍니다. (재무·전망은 반영하지 않는 단순 선별이며 추천이 아닙니다)
5. **비상장 기업**: 목록에 없는 이름(예: 토스, 당근마켓, 무신사)을 입력하면 주가 대신 **위키백과 소개와 최신 뉴스**로 분석합니다. 재무 데이터가 없어서 `확인이 더 필요한 정보`를 따로 알려주고, 없는 수치는 지어내지 않습니다.
6. **메일 알림**: 감시할 기업을 정해 두면 주가가 전일 대비 크게 움직이거나, 52주 신고가·신저가에 닿거나, 악재·호재 키워드가 든 **새 뉴스**가 나올 때 메일로 알려줍니다. (AI가 한 줄 요약을 붙입니다)
7. **결과**: 글을 읽지 않아도 보이도록 시각화합니다. 리포트는 `.md` 파일로 내려받을 수 있습니다.
   - 회사 로고와 AI 한 줄 요약 배너, 핵심 지표 카드
   - 6개월 주가 차트(20일 평균선)와 **52주 범위 위치 막대**
   - 긍정 요인 / 위험 요인 / 지켜볼 점 카드
   - **같은 업종 비교 막대 차트** (3개월 · 1개월 · 52주 고점 대비 전환)
   - **뉴스 분위기 도넛 차트**와 감성 색 점이 붙은 뉴스 목록

## 설치 라이브러리

**Python 3.10 이상**이 필요합니다. (`python --version`으로 확인)

```bash
python -m pip install -r requirements.txt
```

| 라이브러리 | 용도 |
|---|---|
| huggingface_hub | Hugging Face 모델 호출 |
| yfinance | 주가·재무 데이터 수집 |
| requests | 뉴스(RSS) 수집 |
| python-dotenv | `.env`에서 키 읽기 |
| schedule | 매일 자동 실행 |
| streamlit | 웹 화면 |

`pip`만 쓰면 다른 버전의 Python에 설치될 수 있어서 `python -m pip`를 권장합니다. Python이 3.10보다 낮다면 새 환경을 만드세요. (Anaconda 예시)
```bash
conda create -n rpa python=3.11 -y
conda activate rpa
python -m pip install -r requirements.txt
```

## 실행 방법

### 1. Hugging Face 토큰 발급
https://huggingface.co/settings/tokens 에서 `Create new token`을 누르고, 토큰 종류에서 **Inference Providers 호출 권한**(Make calls to Inference Providers)을 켭니다.

### 2. `.env` 파일 만들기
`.env.example`을 복사해서 이름을 `.env`로 바꾸고, 발급받은 토큰을 `=` 뒤에 붙여 넣습니다.

```bash
# Windows (PowerShell / CMD)
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

```
HF_TOKEN=hf_여기에_발급받은_토큰
```

- 따옴표(`"`)나 공백 없이 토큰만 그대로 붙여 넣으세요.
- 메일 발송(`--mail`)을 쓸 때만 `MAIL_FROM`, `MAIL_APP_PASSWORD`(구글 앱 비밀번호), `MAIL_TO`를 채우면 됩니다.
- `.env`는 `.gitignore`에 들어 있어 GitHub에 올라가지 않습니다. 토큰을 다른 사람에게 공유하지 마세요.

### 3. 실행하기

**웹 화면으로 실행 (추천)** : 브라우저가 자동으로 열립니다.
```bash
streamlit run app.py
```
위쪽 탭에서 `기업 분석`(왼쪽에서 기업을 고르고 `분석 시작`)과 `오늘의 관심 종목`을 볼 수 있습니다. 기업은 (국내외 대표 기업 85개를 이름으로 검색할 수 있고, 목록에 없으면 티커를 직접 입력, 예: `AAPL`, `035420.KS`) 한 번에 최대 3개까지 분석합니다. 로고는 회사 웹사이트 아이콘을 불러오며, 없으면 이름의 첫 글자로 표시됩니다.

**주소로 바로 열기**: 주소 끝에 `?names=기업명`을 붙이면 선택 없이 바로 분석됩니다. (예: `http://localhost:8501/?names=삼성전자,토스`)

**터미널로 실행**
```bash
python 261020_bucheon_hugging_jbs.py 삼성전자 SK하이닉스      # 바로 분석 → reports/ 폴더에 .md 저장
python 261020_bucheon_hugging_jbs.py AAPL --mail             # 분석 후 메일 발송
python 261020_bucheon_hugging_jbs.py 삼성전자 --daily 09:00   # 매일 09:00에 자동 실행 (종료: Ctrl+C)
```

### 4. 메일 알림 켜기 (선택)

기업에 변화나 이슈가 생기면 메일로 받을 수 있습니다.

1. `.env`에 `MAIL_FROM`(보내는 Gmail), `MAIL_APP_PASSWORD`(구글 [앱 비밀번호](https://myaccount.google.com/apppasswords), 2단계 인증 필요), `MAIL_TO`(받는 주소)를 채웁니다.
2. 웹 화면의 `알림` 탭에서 감시할 기업과 주가 급변 기준(%)을 고르고 `설정 저장`을 누릅니다. `테스트 메일 보내기`로 먼저 확인해 보세요.
3. 계속 점검하려면 터미널에서 실행해 두세요. 웹 화면을 닫아도 동작합니다.
```bash
python 261020_bucheon_hugging_jbs.py --watch 30                  # 30분마다 점검 (저장한 설정 사용)
python 261020_bucheon_hugging_jbs.py 삼성전자 토스 --watch 30     # 기업을 직접 지정
python 261020_bucheon_hugging_jbs.py --once                      # 한 번만 점검 (Windows 작업 스케줄러용)
python 261020_bucheon_hugging_jbs.py --once --dry-run            # 메일은 보내지 않고 결과만 확인
```
- **처음 점검한 기업은 기준만 저장**하고, 다음 점검부터 변화를 알려줍니다. 같은 날 같은 알림은 한 번만 보냅니다.
- 뉴스는 제목에 `파업`, `소송`, `급락` 같은 악재 키워드나 `수주`, `사상 최대` 같은 호재 키워드가 든 새 기사만 골라 알립니다. 키워드는 코드의 `RISK_WORDS`, `GOOD_WORDS`에서 바꿀 수 있습니다.
- 점검 기록은 `alerts_state.json`, 감시 설정은 `alerts.json`에 저장되며 GitHub에는 올라가지 않습니다.
- ⚠️ 웹사이트를 **누구나 접속하는 주소로 배포**할 때는 `MAIL_*`를 Secrets에 넣지 마세요. 방문자가 알림 버튼으로 내 메일함에 메일을 보낼 수 있습니다. 알림은 내 컴퓨터에서 실행하는 용도로 권장합니다.

> **참고: 무료 크레딧**
> Hugging Face 무료 계정은 매달 제공되는 크레딧이 적습니다. 분석 1건마다 모델을 1번 호출하므로 많이 쓰면 `402` 오류가 날 수 있습니다. 웹 화면은 같은 기업의 결과를 잠시 저장해서 호출을 아낍니다.

## 문제가 생겼을 때

| 증상 | 해결 |
|---|---|
| `KeyError: 'HF_TOKEN'` 또는 `401` | `.env`가 없거나 토큰이 잘못됐습니다. 파일 이름이 `.env`인지, 토큰 앞뒤에 공백·따옴표가 없는지 확인하세요. |
| `402` / 크레딧 소진 | 이번 달 무료 크레딧을 다 쓴 것입니다. 다음 달에 다시 쓰거나 `.env`의 `HF_MODEL`을 다른 모델로 바꿔 보세요. |
| `메일 설정이 없습니다` / 알림 탭이 안내만 보임 | `.env`에 `MAIL_FROM`, `MAIL_APP_PASSWORD`, `MAIL_TO`를 모두 채우세요. 일반 비밀번호가 아니라 구글 **앱 비밀번호**여야 합니다. |
| 상장사인데 `비상장 · 주가 정보 없음`으로 나옴 | 목록에 없는 상장사는 이름만으로 주가를 찾지 못합니다. 티커를 직접 입력하세요. (한국: 종목코드 + `.KS`/`.KQ`, 예: `035420.KS`, 미국: `AAPL`) |
| `No matching distribution found ...` | Python 버전이 3.10보다 낮습니다. 위의 새 환경을 만든 뒤 `python -m pip install -r requirements.txt`를 다시 실행하세요. |
| `No module named ...` | `python -m pip install -r requirements.txt`를 다시 실행하세요. 설치한 Python과 실행하는 Python이 같은지 확인하세요. |
