"""기업 분석 RPA (Hugging Face 모델 사용)

기업명 -> 주가/재무/뉴스 자동 수집 -> 허깅페이스 모델이 분석 -> 리포트(.md) 저장 -> (선택) 메일 발송

사용 예
    python 261020_bucheon_hugging_jbs.py 삼성전자 SK하이닉스      # 바로 분석
    python 261020_bucheon_hugging_jbs.py 삼성전자 --mail          # 분석 후 메일 발송
    python 261020_bucheon_hugging_jbs.py 삼성전자 --daily 09:00   # 매일 09:00에 자동 실행
    python 261020_bucheon_hugging_jbs.py AAPL                     # 티커도 가능

필요한 것
    pip install huggingface_hub yfinance requests python-dotenv schedule
    .env: HF_TOKEN=...  (메일 발송 시 MAIL_FROM, MAIL_APP_PASSWORD, MAIL_TO)
"""

import argparse
import base64
import json
import os
import re
import smtplib
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape as html_escape
from pathlib import Path
from urllib.parse import quote, urlparse

import requests
import yfinance as yf
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_MODEL = os.getenv("HF_MODEL", "deepseek-ai/DeepSeek-V4.1-Flash")
REPORT_DIR = Path(__file__).parent / "reports"
NEWS_COUNT = 8
UNLISTED_NEWS_COUNT = 15

# 이름으로 바로 찾을 수 있는 기업 (그 외에는 티커를 직접 입력: 예 AAPL, 035420.KS)
KR_TICKERS = {
    # 반도체·IT
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "삼성전기": "009150.KS",
    "삼성SDS": "018260.KS", "한미반도체": "042700.KS", "LG전자": "066570.KS",
    "NAVER": "035420.KS", "네이버": "035420.KS", "카카오": "035720.KS",
    # 자동차
    "현대차": "005380.KS", "현대자동차": "005380.KS", "기아": "000270.KS",
    "현대모비스": "012330.KS", "현대글로비스": "086280.KS",
    # 배터리·소재
    "LG에너지솔루션": "373220.KS", "삼성SDI": "006400.KS", "LG화학": "051910.KS",
    "POSCO홀딩스": "005490.KS", "포스코홀딩스": "005490.KS", "포스코퓨처엠": "003670.KS",
    "고려아연": "010130.KS", "롯데케미칼": "011170.KS", "에코프로": "086520.KQ",
    "에코프로비엠": "247540.KQ",
    # 바이오·헬스
    "삼성바이오로직스": "207940.KS", "셀트리온": "068270.KS", "알테오젠": "196170.KQ",
    "HLB": "028300.KQ",
    # 금융
    "KB금융": "105560.KS", "신한지주": "055550.KS", "하나금융지주": "086790.KS",
    "우리금융지주": "316140.KS", "카카오뱅크": "323410.KS", "삼성생명": "032830.KS",
    "삼성화재": "000810.KS",
    # 조선·방산·에너지·인프라
    "한화에어로스페이스": "012450.KS", "HD현대중공업": "329180.KS", "한화오션": "042660.KS",
    "두산에너빌리티": "034020.KS", "SK이노베이션": "096770.KS", "한국전력": "015760.KS",
    "삼성물산": "028260.KS", "현대건설": "000720.KS",
    # 통신·게임·엔터
    "SK텔레콤": "017670.KS", "KT": "030200.KS", "크래프톤": "259960.KS",
    "엔씨소프트": "036570.KS", "넷마블": "251270.KS", "펄어비스": "263750.KQ",
    "하이브": "352820.KS",
    # 소비재·유통·항공
    "대한항공": "003490.KS", "CJ제일제당": "097950.KS", "아모레퍼시픽": "090430.KS",
    "LG생활건강": "051900.KS", "농심": "004370.KS", "오리온": "271560.KS",
    "이마트": "139480.KS",
}

US_TICKERS = {
    "애플": "AAPL", "마이크로소프트": "MSFT", "엔비디아": "NVDA", "구글": "GOOGL",
    "알파벳": "GOOGL", "아마존": "AMZN", "메타": "META", "테슬라": "TSLA",
    "넷플릭스": "NFLX", "AMD": "AMD", "인텔": "INTC", "브로드컴": "AVGO",
    "TSMC": "TSM", "오라클": "ORCL", "어도비": "ADBE", "세일즈포스": "CRM",
    "팔란티어": "PLTR", "JP모건": "JPM", "비자": "V", "마스터카드": "MA",
    "버크셔해서웨이": "BRK-B", "월마트": "WMT", "코스트코": "COST", "코카콜라": "KO",
    "펩시": "PEP", "맥도날드": "MCD", "스타벅스": "SBUX", "나이키": "NKE",
    "디즈니": "DIS", "쿠팡": "CPNG", "보잉": "BA", "엑슨모빌": "XOM", "존슨앤존슨": "JNJ",
}

TICKERS = {**KR_TICKERS, **US_TICKERS}

# 같은 업종 비교용 분류 (이름은 위 목록의 이름과 같아야 함)
SECTORS = {
    "반도체": ["삼성전자", "SK하이닉스", "한미반도체", "삼성전기", "엔비디아", "AMD", "인텔", "브로드컴", "TSMC"],
    "인터넷·플랫폼": ["NAVER", "카카오", "구글", "메타", "아마존", "넷플릭스"],
    "소프트웨어·IT서비스": ["삼성SDS", "마이크로소프트", "오라클", "어도비", "세일즈포스", "팔란티어"],
    "전자·기기": ["삼성전자", "LG전자", "애플"],
    "자동차": ["현대차", "기아", "현대모비스", "현대글로비스", "테슬라"],
    "배터리·소재": ["LG에너지솔루션", "삼성SDI", "LG화학", "포스코퓨처엠", "에코프로", "에코프로비엠",
                  "롯데케미칼", "POSCO홀딩스", "고려아연"],
    "바이오·제약": ["삼성바이오로직스", "셀트리온", "알테오젠", "HLB", "존슨앤존슨"],
    "금융": ["KB금융", "신한지주", "하나금융지주", "우리금융지주", "카카오뱅크", "삼성생명", "삼성화재",
           "JP모건", "비자", "마스터카드", "버크셔해서웨이"],
    "조선·방산": ["한화에어로스페이스", "HD현대중공업", "한화오션", "보잉"],
    "에너지·전력·건설": ["두산에너빌리티", "SK이노베이션", "한국전력", "현대건설", "삼성물산", "엑슨모빌"],
    "통신": ["SK텔레콤", "KT"],
    "게임·엔터·미디어": ["크래프톤", "엔씨소프트", "넷마블", "펄어비스", "하이브", "디즈니", "넷플릭스"],
    "식품·외식": ["농심", "오리온", "CJ제일제당", "코카콜라", "펩시", "맥도날드", "스타벅스"],
    "화장품·생활용품": ["아모레퍼시픽", "LG생활건강"],
    "패션·스포츠": ["나이키"],
    "유통·이커머스": ["이마트", "월마트", "코스트코", "쿠팡", "아마존"],
    "항공·물류": ["대한항공", "현대글로비스"],
}


client = InferenceClient(api_key=os.environ.get("HF_TOKEN"))


# ---------- 1. 수집 ----------
def find_ticker(name):
    if name in TICKERS:
        return TICKERS[name]
    if name.isascii() and " " not in name:  # 이미 티커 형태 (AAPL, 035420.KS)
        return name.upper()
    quotes = yf.Search(name, max_results=1).quotes  # 영문 회사명 검색
    if quotes:
        return quotes[0]["symbol"]
    raise ValueError(f"'{name}' 티커를 찾지 못했습니다. 티커를 직접 입력해 주세요. (예: 005930.KS)")


def get_stock(ticker):
    """주가와 주요 재무 지표를 가져온다."""
    t = yf.Ticker(ticker)
    info = t.info
    hist = t.history(period="3mo")["Close"]
    change = lambda days: (hist.iloc[-1] / hist.iloc[-days] - 1) * 100 if len(hist) > days else None
    return {
        "회사명": info.get("longName") or ticker,
        "업종": info.get("industry") or info.get("sector"),
        "웹사이트": info.get("website"),
        "통화": info.get("currency"),
        "현재가": info.get("currentPrice") or float(hist.iloc[-1]),
        "시가총액": info.get("marketCap"),
        "PER": info.get("trailingPE"),
        "PBR": info.get("priceToBook"),
        "배당수익률(%)": info.get("dividendYield"),
        "52주 최고": info.get("fiftyTwoWeekHigh"),
        "52주 최저": info.get("fiftyTwoWeekLow"),
        "최근 1주 등락(%)": change(5),
        "최근 1개월 등락(%)": change(21),
        "최근 3개월 등락(%)": change(len(hist) - 1),
    }


def get_history(ticker, period="6mo"):
    """차트용 종가 데이터를 가져온다."""
    return yf.Ticker(ticker).history(period=period)["Close"]


def get_logo(ticker):
    """회사 웹사이트 주소로 로고(파비콘)를 받아 data URI로 돌려준다. 없으면 None."""
    try:
        site = yf.Ticker(ticker).info.get("website") or ""
    except Exception:
        return None
    domain = urlparse(site).netloc.replace("www.", "")
    if not domain:
        return None
    sources = (
        (f"https://www.google.com/s2/favicons?domain={domain}&sz=128", 400),
        (f"https://icons.duckduckgo.com/ip3/{domain}.ico", 600),
    )
    for url, min_size in sources:  # 너무 작은 파일은 기본 아이콘이라 건너뛴다
        try:
            res = requests.get(url, timeout=6)
        except requests.RequestException:
            continue
        kind = res.headers.get("content-type", "")
        if res.ok and kind.startswith("image") and len(res.content) > min_size:
            return f"data:{kind};base64,{base64.b64encode(res.content).decode()}"
    return None


def market_snapshot(names):
    """여러 기업의 최근 1년 주가를 한 번에 받아 등락률 등을 계산한다."""
    tickers = {}
    for n in names:
        tickers.setdefault(TICKERS[n], n)  # 같은 회사의 다른 이름은 하나만
    df = yf.download(list(tickers), period="1y", progress=False, auto_adjust=True, group_by="ticker")
    rows = []
    for t, n in tickers.items():
        try:
            close = df[t]["Close"].dropna()
        except KeyError:
            continue
        if len(close) < 30:
            continue
        last = float(close.iloc[-1])
        rows.append({
            "name": n,
            "ticker": t,
            "price": last,
            "currency": "KRW" if t.endswith((".KS", ".KQ")) else "USD",
            "ch1m": (last / float(close.iloc[-22]) - 1) * 100 if len(close) > 22 else None,
            "ch3m": (last / float(close.iloc[-64]) - 1) * 100 if len(close) > 64 else None,
            "from_high": (last / float(close.max()) - 1) * 100,
        })
    return rows


def sector_of(name):
    """기업이 속한 업종 이름들을 돌려준다. (예: 농심 -> ['식품·외식'])"""
    ticker = TICKERS.get(name)
    return [sec for sec, members in SECTORS.items() if any(TICKERS.get(m) == ticker for m in members)] if ticker else []


def peers_of(name, limit=4):
    """같은 업종의 다른 기업 이름을 돌려준다 (같은 시장을 먼저)."""
    ticker = TICKERS.get(name)
    if not ticker:
        return []
    is_kr = ticker.endswith((".KS", ".KQ"))
    found = {}
    for members in SECTORS.values():
        if any(TICKERS.get(m) == ticker for m in members):
            for m in members:
                t = TICKERS.get(m)
                if t and t != ticker:
                    found.setdefault(t, m)
    names = sorted(found.values(), key=lambda m: TICKERS[m].endswith((".KS", ".KQ")) != is_kr)
    return names[:limit]


def screen_candidates(rows, top=5):
    """가격 흐름만 보고 관심 후보를 고른다. (재무·전망은 반영하지 않는 단순 선별)"""
    with_3m = [r for r in rows if r["ch3m"] is not None]
    return {
        "momentum": sorted(with_3m, key=lambda r: r["ch3m"], reverse=True)[:top],
        "dip": sorted(rows, key=lambda r: r["from_high"])[:top],
    }


def get_news(keyword, count=NEWS_COUNT):
    """구글 뉴스 RSS에서 최신 기사 제목을 가져온다."""
    url = f"https://news.google.com/rss/search?q={quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return [
        {"title": i.findtext("title"), "date": i.findtext("pubDate")}
        for i in ET.fromstring(res.content).findall(".//item")[:count]
    ]


# ---------- 2. 분석 ----------
def fmt(v):
    if v is None:
        return "정보 없음"
    if isinstance(v, (int, float)) and abs(v) >= 1e12:  # 큰 금액은 조 단위로
        return f"{v / 1e12:,.1f}조"
    return f"{v:,.2f}" if isinstance(v, float) else f"{v:,}" if isinstance(v, int) else str(v)


def call_model(prompt):
    """허깅페이스 모델에 질문을 보내고 답변을 받는다."""
    res = client.chat.completions.create(
        model=HF_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=6000,  # 추론형 모델이라 생각하는 데도 토큰을 쓴다
        temperature=0.3,
    )
    text = res.choices[0].message.content
    if not text:  # 추론에 토큰을 다 써서 답변이 비는 경우
        raise RuntimeError("모델이 빈 답변을 돌려줬습니다. 다시 시도하거나 HF_MODEL을 바꿔 보세요.")
    if res.choices[0].finish_reason == "length":
        text += "\n\n(※ 답변이 길이 제한으로 중간에 끊겼습니다)"
    return text


WIKI_HEADERS = {"User-Agent": "company-analysis-rpa/1.0 (student project)"}
COMPANY_WORDS = ("회사", "기업", "플랫폼", "스타트업", "업체", "company", "startup", "corporation")


SENTIMENTS = ("긍정", "중립", "부정")


def ask_json(prompt, news_count=0):
    """모델에게 JSON 답변을 받는다. 형식이 틀리면 한 번 더 시도하고, 끝내 안 되면 원문을 돌려준다."""
    text = ""
    for _ in range(2):
        text = call_model(prompt)
        try:
            data = json.loads(re.search(r"\{.*\}", text, re.DOTALL).group())
        except (AttributeError, ValueError):
            continue
        sentiment = [s if s in SENTIMENTS else "중립" for s in data.get("news_sentiment", [])]
        data["news_sentiment"] = (sentiment + ["중립"] * news_count)[:news_count]  # 뉴스 개수에 맞춘다
        return data
    return {"raw": text}


def money(v, ticker):
    """가격을 보기 좋게: 한국 종목은 '211,500원', 그 외는 '$217.09'."""
    return f"{v:,.0f}원" if ticker.endswith((".KS", ".KQ")) else f"${v:,.2f}"


def analyze(name, stock, news, peers=None):
    """수집한 데이터를 허깅페이스 모델에게 주고 분석 결과(JSON)를 받는다."""
    stock_text = "\n".join(f"- {k}: {fmt(v)}" for k, v in stock.items())
    news_text = "\n".join(f"{i}. {n['title']}" for i, n in enumerate(news, 1))
    peer_text = "\n".join(
        f"- {p['name']}: 1개월 {fmt(p['ch1m'])}%, 3개월 {fmt(p['ch3m'])}%, 52주 고점 대비 {fmt(p['from_high'])}%"
        for p in (peers or [])
    )
    peer_part = f"\n[같은 업종 기업의 주가 흐름]\n{peer_text}\n" if peer_text else ""
    peer_field = ',\n  "peer_notes": {"기업명": "그 기업과 비교한 한 줄(20자 이내)"}' if peer_text else ""
    prompt = f"""아래 데이터만 근거로 '{name}' 기업 분석 결과를 JSON 하나로만 출력해줘. 설명이나 코드블록(```)은 쓰지 마.

[주가·재무]
{stock_text}

[최근 뉴스 제목]
{news_text}
{peer_part}
[출력 형식]
{{
  "summary": "한 줄 요약 (50자 이내)",
  "positives": ["긍정 요인 (25자 이내)", ...최대 3개],
  "risks": ["위험 요인 (25자 이내)", ...최대 3개],
  "watch": ["앞으로 지켜볼 점 (20자 이내)", ...최대 3개],
  "news_sentiment": ["긍정|중립|부정", ...뉴스 {len(news)}개 순서대로 하나씩]{peer_field}
}}

[규칙]
- 데이터에 없는 수치나 사실은 지어내지 마. 모르면 항목을 비워 둬.
- 문장은 짧은 명사구로 써. 긴 설명은 금지.
- news_sentiment는 해당 기업 입장에서 뉴스가 호재면 긍정, 악재면 부정, 아니면 중립.
- 매수/매도/목표가 같은 투자 권유는 절대 하지 마."""
    return ask_json(prompt, len(news))


def resolve(name):
    """기업명을 상장사(티커)와 비상장사로 구분한다. -> ("listed", 티커) / ("unlisted", None)"""
    if name in TICKERS:
        return "listed", TICKERS[name]
    if name.isascii() and " " not in name:  # AAPL, 035420.KS 같은 티커 형태
        try:
            if not yf.Ticker(name.upper()).history(period="5d").empty:
                return "listed", name.upper()
        except Exception:
            pass
    try:  # 영문 회사명 검색
        if name.isascii():
            key = name.lower().replace(" ", "")
            for q in yf.Search(name, max_results=5).quotes:  # 이름이 실제로 비슷한 주식만 인정
                label = (q.get("longname", "") + q.get("shortname", "")).lower().replace(" ", "")
                if q.get("quoteType") == "EQUITY" and key in label:
                    return "listed", q["symbol"]
    except Exception:
        pass
    return "unlisted", None


def wiki_get(url, params=None):
    """위키백과 API를 호출한다. 일시적인 실패는 몇 번 다시 시도하고, 끝내 실패하면 None."""
    for attempt in range(3):
        try:
            res = requests.get(url, params=params, headers=WIKI_HEADERS, timeout=8)
            if res.ok:
                return res.json()
            if res.status_code == 404:
                return None
        except (requests.RequestException, ValueError):
            pass
        time.sleep(0.7 * (attempt + 1))
    return None


def wiki_page(lang, title):
    """위키백과 문서 요약을 가져온다. 실패하면 None."""
    return wiki_get(f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'), safe='')}")


def get_wiki(name):
    """위키백과에서 회사 소개를 찾는다. 엉뚱한 문서(동음이의어 등)는 걸러내고, 못 찾으면 None."""
    key = name.lower().replace(" ", "")
    for lang in ("ko", "en"):
        search = wiki_get(
            f"https://{lang}.wikipedia.org/w/api.php",
            {"action": "query", "list": "search", "srsearch": f"{name} 회사" if lang == "ko" else name,
             "format": "json", "srlimit": 8},
        )
        hits = (search or {}).get("query", {}).get("search", [])
        for hit in hits:  # 한 문서가 실패해도 다음 문서를 계속 확인한다
            page = wiki_page(lang, hit["title"])
            if not page:
                continue
            text = (page.get("description") or "") + " " + (page.get("extract") or "")
            if "동음이의" in text or key not in (page.get("title", "") + text).lower().replace(" ", ""):
                continue
            if not any(w in text.lower() for w in COMPANY_WORDS):
                continue
            return {
                "제목": page.get("title"),
                "소개": page.get("extract"),
                "설명": page.get("description"),
                "이미지": (page.get("thumbnail") or {}).get("source"),
                "링크": (page.get("content_urls") or {}).get("desktop", {}).get("page"),
            }
    return None


def get_image_uri(url):
    """이미지 주소를 받아 data URI로 바꾼다. 실패하면 None."""
    try:
        res = requests.get(url, headers=WIKI_HEADERS, timeout=8)
        kind = res.headers.get("content-type", "")
        if res.ok and kind.startswith("image"):
            return f"data:{kind};base64,{base64.b64encode(res.content).decode()}"
    except requests.RequestException:
        pass
    return None


def analyze_unlisted(name, wiki, news):
    """비상장 기업: 위키 소개와 뉴스만으로 분석한다. (주가·재무 데이터 없음)"""
    wiki_text = f"{wiki['제목']}: {wiki['소개']}" if wiki else "찾지 못함"
    news_text = "\n".join(f"{i}. {n['title']}" for i, n in enumerate(news, 1)) or "뉴스를 찾지 못함"
    prompt = f"""'{name}'은(는) 주식시장에 상장되지 않은 기업일 수 있어 주가·재무 데이터가 없어.
아래 자료만 근거로 기업 분석 결과를 JSON 하나로만 출력해줘. 설명이나 코드블록(```)은 쓰지 마.

[위키백과 소개 (다른 기업 문서일 수 있으니 뉴스와 맞지 않으면 무시)]
{wiki_text}

[최근 뉴스 제목]
{news_text}

[출력 형식]
{{
  "summary": "한 줄 요약 (50자 이내)",
  "about": "어떤 회사인지 (60자 이내)",
  "issues": ["최근 이슈 (25자 이내)", ...최대 3개],
  "risks": ["위험 요인 (25자 이내)", ...최대 3개],
  "watch": ["앞으로 지켜볼 점 (20자 이내)", ...최대 3개],
  "need_check": ["직접 확인이 필요한 정보 (15자 이내)", ...최대 5개],
  "news_sentiment": ["긍정|중립|부정", ...뉴스 {len(news)}개 순서대로 하나씩]
}}

[규칙]
- 자료에 없는 사실(매출, 투자 유치 금액, 기업가치, 직원 수 등)은 절대 지어내지 마. 모르면 항목을 비워 둬.
- need_check에는 공시, 감사보고서, 투자 유치 현황처럼 직접 확인해야 할 항목을 써.
- 문장은 짧은 명사구로 써. 긴 설명은 금지.
- 투자 권유는 하지 마."""
    return ask_json(prompt, len(news))


# ---------- 3. 저장 / 발송 ----------
def bullets(items):
    return "\n".join(f"- {i}" for i in items) if items else "- 정보 없음"


def analysis_to_md(data, unlisted=False):
    """분석 결과(JSON)를 마크다운 문장으로 바꾼다. (리포트 파일·메일용)"""
    if "raw" in data:
        return data["raw"]
    parts = [f"## 한 줄 요약\n{data.get('summary', '정보 없음')}"]
    if unlisted:
        parts.append(f"## 어떤 회사인가\n{data.get('about', '정보 없음')}")
        parts.append(f"## 최근 이슈\n{bullets(data.get('issues'))}")
    else:
        parts.append(f"## 긍정 요인\n{bullets(data.get('positives'))}")
    parts.append(f"## 위험 요인\n{bullets(data.get('risks'))}")
    parts.append(f"## 앞으로 지켜볼 점\n{bullets(data.get('watch'))}")
    if unlisted:
        parts.append(f"## 확인이 더 필요한 정보\n{bullets(data.get('need_check'))}")
    elif data.get("peer_notes"):
        notes = [f"{k}: {v}" for k, v in data["peer_notes"].items()]
        parts.append(f"## 함께 볼 만한 종목\n{bullets(notes)}")
    return "\n\n".join(parts)


def build_report(name, ticker, stock, news, analysis):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    stock_rows = "\n".join(f"| {k} | {fmt(v)} |" for k, v in stock.items())
    news_rows = "\n".join(
        f"- [{s}] {n['title']}" for n, s in zip(news, analysis.get("news_sentiment") or ["중립"] * len(news))
    )
    return (
        f"# {name} ({ticker}) 기업 분석 리포트\n\n"
        f"작성: {now} · 모델: {HF_MODEL}\n\n"
        f"{analysis_to_md(analysis)}\n\n"
        f"---\n\n## 수집 데이터\n\n| 항목 | 값 |\n|---|---|\n{stock_rows}\n\n"
        f"### 최근 뉴스\n{news_rows}\n\n"
        "> 이 리포트는 AI가 공개 데이터를 요약한 참고 자료이며 투자 권유가 아닙니다.\n"
    )


def build_report_unlisted(name, wiki, news, analysis):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    news_rows = "\n".join(
        f"- [{s}] {n['title']}" for n, s in zip(news, analysis.get("news_sentiment") or ["중립"] * len(news))
    )
    source = f"- 위키백과: [{wiki['제목']}]({wiki['링크']})\n" if wiki else ""
    return (
        f"# {name} (비상장·주가 정보 없음) 기업 분석 리포트\n\n"
        f"작성: {now} · 모델: {HF_MODEL}\n\n"
        f"{analysis_to_md(analysis, unlisted=True)}\n\n"
        f"---\n\n## 참고 자료\n{source}\n### 최근 뉴스\n{news_rows}\n\n"
        "> 이 리포트는 AI가 공개된 뉴스와 소개글만 요약한 참고 자료입니다. 재무 정보는 없으며 투자 권유가 아닙니다.\n"
    )


def save_report(name, report):
    REPORT_DIR.mkdir(exist_ok=True)
    path = REPORT_DIR / f"{datetime.now():%Y%m%d}_{name}.md"
    path.write_text(report, encoding="utf-8")
    return path


def mail_ready():
    """메일 발송에 필요한 .env 값이 모두 있는지 확인한다."""
    return all(os.getenv(k) for k in ("MAIL_FROM", "MAIL_APP_PASSWORD", "MAIL_TO"))


def send_mail(subject, body, html=None):
    """메일을 보낸다. html을 주면 본문을 HTML로, 못 보는 환경을 위해 글(body)도 함께 담는다."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = os.environ["MAIL_FROM"]
    msg["To"] = os.environ["MAIL_TO"]
    msg.attach(MIMEText(body, "plain", "utf-8"))
    if html:
        msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["MAIL_FROM"], os.environ["MAIL_APP_PASSWORD"])
        server.send_message(msg)


# ---------- 4. 변화·이슈 알림 ----------
STATE_FILE = Path(__file__).parent / "alerts_state.json"  # 이미 본 뉴스·보낸 알림 기록
SETTINGS_FILE = Path(__file__).parent / "alerts.json"  # 감시할 기업과 기준
DEFAULT_THRESHOLD = 3.0
RISK_WORDS = ("급락", "하락세", "적자", "소송", "리콜", "압수수색", "횡령", "배임", "상장폐지", "감사의견", "파업",
              "제재", "과징금", "화재", "사고", "유출", "해킹", "부도", "법정관리", "하향", "철수", "중단", "논란", "의혹")
GOOD_WORDS = ("급등", "사상 최대", "최대 실적", "흑자", "수주", "인수", "승인", "상향", "신고가", "계약 체결", "투자 유치", "호실적")


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_settings():
    return read_json(SETTINGS_FILE, {"companies": [], "threshold": DEFAULT_THRESHOLD})


def save_settings(companies, threshold):
    write_json(SETTINGS_FILE, {"companies": list(companies), "threshold": float(threshold)})


def classify_title(title):
    """뉴스 제목에서 악재/호재 키워드를 찾는다. 악재가 우선."""
    if any(w in title for w in RISK_WORDS):
        return "risk"
    if any(w in title for w in GOOD_WORDS):
        return "good"
    return None


def check_company(name, state, threshold):
    """한 기업의 변화(주가 급변·신고가/신저가·새 이슈 뉴스)를 점검한다. 처음 보는 기업은 기준만 저장한다."""
    kind, ticker = resolve(name)
    today = f"{datetime.now():%Y-%m-%d}"
    mem = state.setdefault(name, {})
    first_run = "seen" not in mem
    seen, alerted = set(mem.get("seen", [])), set(mem.get("alerted", []))
    events, info = [], {"name": name, "ticker": ticker, "kind": kind}

    if kind == "listed":
        close = yf.Ticker(ticker).history(period="1y")["Close"].dropna()
        last, prev = float(close.iloc[-1]), float(close.iloc[-2])
        day = (last / prev - 1) * 100
        info.update(price=last, day=day, currency="KRW" if ticker.endswith((".KS", ".KQ")) else "USD")
        candidates = []
        if abs(day) >= threshold:
            candidates.append(("price", f"{'급등' if day > 0 else '급락'} {day:+.2f}%", f"전일 종가 대비 · 현재가 {money(last, ticker)}"))
        if last >= float(close.max()) * 0.995:
            candidates.append(("high", "52주 신고가 부근", f"현재가 {money(last, ticker)}"))
        elif last <= float(close.min()) * 1.005:
            candidates.append(("low", "52주 신저가 부근", f"현재가 {money(last, ticker)}"))
        for kind_, title, detail in candidates:
            if f"{today}:{kind_}" not in alerted:  # 같은 날 같은 알림은 한 번만
                events.append({"type": kind_, "title": title, "detail": detail})
                alerted.add(f"{today}:{kind_}")

    news = get_news(name, NEWS_COUNT if kind == "listed" else UNLISTED_NEWS_COUNT)
    if not first_run:
        issues = [{"title": n["title"], "tag": classify_title(n["title"])} for n in news if n["title"] not in seen]
        issues = [i for i in issues if i["tag"]]
        if issues:
            events.append({"type": "news", "title": f"새 이슈 뉴스 {len(issues)}건", "items": issues})

    mem.update(seen=sorted(seen | {n["title"] for n in news})[-300:], alerted=sorted(alerted)[-50:],
               checked=datetime.now().isoformat(timespec="seconds"))
    info["first_run"] = first_run
    return events, info


def summarize_events(name, events):
    """알림 내용을 한 줄로 요약한다. 실패하면 빈 문자열."""
    lines = []
    for e in events:
        lines.append(f"- {e['title']}")
        lines += [f"  · [{i['tag']}] {i['title']}" for i in e.get("items", [])]
    prompt = f"""'{name}'에 대해 아래 변화가 감지됐어. 투자자가 메일에서 바로 이해할 수 있게 한 줄(60자 이내)로 요약해줘.
사실만 쓰고, 매수/매도 같은 투자 권유와 없는 내용은 쓰지 마. 요약 문장만 출력해.

{chr(10).join(lines)}"""
    try:
        return call_model(prompt).strip().splitlines()[0]
    except Exception:
        return ""


TAG_STYLE = {"risk": ("#C2410C", "#FFF1E5", "악재"), "good": ("#15803D", "#E8F7EE", "호재")}
EVENT_ICON = {"price": "⚡", "high": "📈", "low": "📉", "news": "📰"}


def build_alert_mail(results):
    """results: [(info, events, summary)] -> (제목, 글 본문, HTML 본문)"""
    names = [r[0]["name"] for r in results]
    subject = f"[기업 알림] {', '.join(names[:3])}{' 외' if len(names) > 3 else ''} 변화 감지 ({datetime.now():%m/%d %H:%M})"
    text, cards = [], []
    for info, events, summary in results:
        head = info["name"] + (f" ({info['ticker']})" if info.get("ticker") else " (비상장)")
        text.append(head)
        card = [f'<div style="font-size:18px;font-weight:700;color:#14213D">{html_escape(head)}</div>']
        if summary:
            text.append(f"  요약: {summary}")
            card.append(f'<div style="margin:6px 0 10px;color:#1B4DB1;font-weight:600">{html_escape(summary)}</div>')
        for e in events:
            text.append(f"  {EVENT_ICON[e['type']]} {e['title']}" + (f" - {e['detail']}" if e.get("detail") else ""))
            card.append(f'<div style="margin-top:8px;font-weight:700">{EVENT_ICON[e["type"]]} {html_escape(e["title"])}</div>')
            if e.get("detail"):
                card.append(f'<div style="color:#6B7A90;font-size:13px">{html_escape(e["detail"])}</div>')
            for i in e.get("items", []):
                color, bg, label = TAG_STYLE[i["tag"]]
                text.append(f"     [{label}] {i['title']}")
                card.append(
                    f'<div style="margin-top:6px;font-size:14px"><span style="background:{bg};color:{color};'
                    f'border-radius:999px;padding:1px 8px;font-size:12px;font-weight:700">{label}</span> '
                    f'{html_escape(i["title"])}</div>'
                )
        cards.append('<div style="background:#fff;border:1px solid #E6EBF2;border-radius:14px;padding:16px 18px;'
                     'margin-bottom:12px">' + "".join(card) + "</div>")
        text.append("")
    text.append("이 알림은 공개 데이터를 자동 점검한 참고 정보이며 투자 권유가 아닙니다.")
    html = (
        '<div style="background:#F4F7FB;padding:20px;font-family:\'Malgun Gothic\',sans-serif">'
        '<div style="max-width:600px;margin:0 auto">'
        '<div style="font-size:20px;font-weight:900;color:#14213D;margin-bottom:12px">📊 기업 변화 알림</div>'
        + "".join(cards)
        + '<div style="color:#8793A6;font-size:12px;margin-top:8px">이 알림은 공개 데이터를 자동 점검한 참고 정보이며 '
        "투자 권유가 아닙니다.</div></div></div>"
    )
    return subject, "\n".join(text), html


def run_alerts(names, threshold=DEFAULT_THRESHOLD, send=True, use_ai=True):
    """기업들을 점검하고, 변화가 있으면 메일을 보낸다. -> (results, 메일 발송 여부)"""
    state = read_json(STATE_FILE, {})
    results = []
    for name in names:
        try:
            events, info = check_company(name, state, threshold)
        except Exception as e:  # 한 기업이 실패해도 나머지는 계속 점검
            print(f"  ✗ {name} 점검 실패: {e}")
            continue
        status = "기준 저장(첫 점검)" if info["first_run"] else (f"변화 {len(events)}건" if events else "변화 없음")
        print(f"  · {name}: {status}")
        if events:
            results.append((info, events, summarize_events(name, events) if use_ai else ""))
    write_json(STATE_FILE, state)
    if results and send:
        subject, text, html = build_alert_mail(results)
        send_mail(subject, text, html)
    return results, bool(results and send)


# ---------- 실행 ----------
def run(names, mail=False):
    for name in names:
        print(f"\n▶ {name} 분석 시작")
        try:
            kind, ticker = resolve(name)
            if kind == "unlisted":  # 주가 데이터가 없는 비상장 기업은 위키·뉴스로 분석
                wiki = get_wiki(name)
                news = get_news(name, UNLISTED_NEWS_COUNT)
                print(f"  비상장(또는 주가 정보 없음) 기업으로 처리: 위키 {'있음' if wiki else '없음'}, 뉴스 {len(news)}건 → {HF_MODEL} 분석 중...")
                report = build_report_unlisted(name, wiki, news, analyze_unlisted(name, wiki, news))
            else:
                stock = get_stock(ticker)
                news = get_news(name if not name.isascii() else stock["회사명"])
                peer_names = peers_of(name)
                peers = market_snapshot(peer_names) if peer_names else []
                print(f"  수집 완료 (지표 {len(stock)}개, 뉴스 {len(news)}건, 같은 업종 {len(peers)}곳) → {HF_MODEL} 분석 중...")
                report = build_report(name, ticker, stock, news, analyze(name, stock, news, peers))
        except Exception as e:  # 한 기업이 실패해도 다음 기업은 계속 진행
            print(f"  ✗ 실패: {e}")
            continue
        path = save_report(name, report)
        print(f"  ✓ 리포트 저장: {path}")
        if mail:
            send_mail(f"[기업 분석] {name} {datetime.now():%Y-%m-%d}", report)
            print("  ✓ 메일 발송 완료")


def main():
    parser = argparse.ArgumentParser(description="기업 분석 RPA")
    parser.add_argument("companies", nargs="*", help="기업명 또는 티커 (예: 삼성전자 AAPL)")
    parser.add_argument("--mail", action="store_true", help="분석 후 메일로 발송")
    parser.add_argument("--daily", metavar="HH:MM", help="매일 해당 시각에 자동 실행")
    parser.add_argument("--watch", type=int, metavar="분", help="N분마다 변화·이슈를 점검해 메일 알림 (종료: Ctrl+C)")
    parser.add_argument("--once", action="store_true", help="변화·이슈를 한 번만 점검하고 알림 (작업 스케줄러용)")
    parser.add_argument("--threshold", type=float, help=f"주가 급변 기준 %% (기본 {DEFAULT_THRESHOLD})")
    parser.add_argument("--dry-run", action="store_true", help="알림 메일을 보내지 않고 내용만 출력")
    args = parser.parse_args()

    if args.watch or args.once:  # 알림 모드: 기업을 안 적으면 웹에서 저장한 alerts.json을 쓴다
        settings = load_settings()
        names = args.companies or settings["companies"]
        threshold = args.threshold or settings["threshold"]
        if not names:
            raise SystemExit("감시할 기업이 없습니다. 기업명을 적거나 웹의 '알림' 탭에서 저장하세요.")
        if not args.dry_run and not mail_ready():
            raise SystemExit("메일 설정이 없습니다. .env에 MAIL_FROM, MAIL_APP_PASSWORD, MAIL_TO를 채우세요.")

        def check():
            print(f"\n[{datetime.now():%H:%M:%S}] 점검: {', '.join(names)} (주가 기준 ±{threshold}%)")
            results, sent = run_alerts(names, threshold, send=not args.dry_run)
            if args.dry_run and results:
                print(build_alert_mail(results)[1])
            print("  ✓ 알림 메일 발송" if sent else "  (메일은 보내지 않았습니다)" if args.dry_run and results else "  알림 보낼 변화 없음")

        check()
        while args.watch:
            time.sleep(args.watch * 60)
            check()
        return

    names = args.companies or input("분석할 기업명(띄어쓰기로 여러 개): ").split()
    if not names:
        return

    if args.daily:
        import schedule

        schedule.every().day.at(args.daily).do(run, names, args.mail)
        print(f"매일 {args.daily}에 {', '.join(names)} 분석을 실행합니다. (종료: Ctrl+C)")
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run(names, args.mail)


if __name__ == "__main__":
    main()
