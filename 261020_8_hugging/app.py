import math
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html import escape
from importlib import import_module

import altair as alt
import pandas as pd
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# 배포 환경(Streamlit Cloud)에서는 .env 대신 Secrets에서 키를 가져온다
for key in ("HF_TOKEN", "HF_MODEL"):
    try:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]
    except Exception:
        pass  # 로컬에 secrets.toml이 없으면 .env를 사용

# 모듈 이름이 숫자로 시작해서 import_module로 불러온다
core = import_module("261020_bucheon_hugging_jbs")

UP, DOWN = "#E5484D", "#2F6FED"  # 한국식: 상승 빨강, 하락 파랑
SENT_COLOR = {"긍정": "#22A06B", "중립": "#CBD5E1", "부정": "#F97316"}
MAX_COMPANIES = 3

st.set_page_config(page_title="기업 분석 RPA", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    html, body, [class*="css"], .stMarkdown, button, input, textarea {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-top: 4.5rem; padding-bottom: 3rem; max-width: 1100px;}
    [data-testid="stHeader"] {background: transparent;}
    .app-head {margin: .2rem 0 1.1rem;}
    .app-title {font-size: 1.7rem; font-weight: 900; color: #14213D; letter-spacing: -.02em;}
    .app-title span {color: #2563EB;}
    .app-sub {color: #6B7A90; font-size: .95rem; margin-top: .15rem;}
    [data-testid="stSidebar"] {background: #FFFFFF; border-right: 1px solid #E8EDF4;}
    [data-testid="stSidebarContent"] {padding: 1.4rem 1rem;}
    .brand {display: flex; align-items: center; gap: .7rem; margin-bottom: 1.6rem;}
    .brand .mark {width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center;
                  justify-content: center; font-size: 1.2rem; color: #fff;
                  background: linear-gradient(135deg, #2563EB 0%, #60A5FA 100%);
                  box-shadow: 0 4px 12px rgba(37,99,235,.28);}
    .brand .bt {font-size: 1.1rem; font-weight: 800; color: #14213D; line-height: 1.2;}
    .brand .bs {font-size: .74rem; color: #8793A6;}
    .side-label {font-size: .74rem; font-weight: 700; color: #8793A6; letter-spacing: .04em; margin-bottom: .4rem;}
    .hint {display: flex; justify-content: space-between; color: #8793A6; font-size: .74rem; margin-top: .35rem;}
    [data-testid="stSidebar"] [data-baseweb="select"] > div {background: #F4F7FB; border: 1px solid transparent;
                                                            border-radius: 12px; min-height: 46px;}
    [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {border-color: #2563EB; background: #fff;}
    [data-testid="stSidebar"] [data-baseweb="tag"] {border-radius: 8px;}
    [data-testid="stSidebar"] button[kind="primary"] {border-radius: 12px; height: 46px; font-weight: 700; border: none;
                                                      box-shadow: 0 4px 12px rgba(37,99,235,.25);}
    [data-testid="stSidebar"] button[kind="primary"]:disabled {background: #EEF2F8; color: #A0AEC0; box-shadow: none;}
    [data-testid="stSidebar"] [data-testid="stExpander"], [data-testid="stSidebar"] [data-testid="stExpander"] details
        {border: none !important; background: transparent !important;}
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {color: #6B7A90; font-size: .85rem; padding-left: 0;}
    [data-testid="stSidebar"] [data-testid="stPills"] button, [data-testid="stSidebar"] [data-testid="stButtonGroup"] button
        {border-radius: 999px; font-size: .82rem; padding: .2rem .75rem; border: 1px solid #E3E9F2; background: #fff;}
    [data-baseweb="tab-list"] {gap: .3rem; border-bottom: 1px solid #E8EDF4;}
    button[data-baseweb="tab"] {border-radius: 10px 10px 0 0; padding: .55rem 1rem; font-weight: 600;}
    [data-baseweb="tab-highlight"] {background-color: #2563EB !important; height: 3px !important;}
    .empty {text-align: center; background: #fff; border: 1px dashed #D5DEEB; border-radius: 20px;
            padding: 2.6rem 1.5rem 2.2rem; margin: 1rem 0; color: #51617A;}
    .empty .icon {font-size: 2.4rem; margin-bottom: .4rem;}
    .empty .etitle {font-size: 1.15rem; font-weight: 800; color: #14213D; margin-bottom: .35rem;}
    .empty .edesc {font-size: .92rem; line-height: 1.7;}
    .empty code {background: #EEF2F8; border-radius: 6px; padding: .05rem .4rem; font-size: .85rem;}
    .rank-row {display: flex; align-items: center; gap: .8rem; background: #fff; border: 1px solid #E8EDF4;
               border-radius: 14px; padding: .65rem .9rem; margin-bottom: .5rem;}
    .rank-row .rank {width: 1.5rem; font-weight: 900; color: #2563EB; text-align: center;}
    .rank-row .grow {flex: 1; min-width: 0;}
    .rank-row .t1 {font-weight: 700; color: #14213D; font-size: .95rem; line-height: 1.2;}
    .rank-row .t2 {color: #6B7A90; font-size: .76rem;}
    .chg3 {font-weight: 800; font-size: 1.05rem; text-align: right; white-space: nowrap;}
    .ev {padding: .35rem 0; color: #2B3A55; font-size: .92rem;} .ev.sub {padding-left: 1.2rem; font-size: .88rem;}
    .ai-line {color: #2563EB; font-weight: 600; margin-bottom: .4rem;}
    .company {display: flex; align-items: center; gap: 1.1rem; background: #fff; border: 1px solid #E6EBF2;
              border-radius: 20px; padding: 1.1rem 1.4rem; margin: .4rem 0 .8rem;
              box-shadow: 0 2px 10px rgba(20,40,80,.06);}
    .company .name {font-size: 1.6rem; font-weight: 900; color: #14213D; line-height: 1.2;}
    .company .meta {color: #6B7A90; font-size: .88rem; margin-top: .2rem;}
    .badge {display: inline-block; background: #EAF0FD; color: #1B4DB1; border-radius: 999px;
            padding: .1rem .6rem; font-size: .76rem; font-weight: 700; margin-right: .3rem;}
    .logo {border-radius: 14px; background: #fff; border: 1px solid #E6EBF2; object-fit: contain; flex: none;}
    .initial {border-radius: 14px; color: #fff; font-weight: 900; display: flex; align-items: center;
              justify-content: center; flex: none;}
    .summary {background: linear-gradient(120deg, #EAF0FD 0%, #F4F8FF 100%); border: 1px solid #D5E2FB;
              border-radius: 16px; padding: 1rem 1.3rem; margin-bottom: 1rem; font-size: 1.12rem;
              font-weight: 700; color: #14213D;}
    .summary small {display: block; color: #1B4DB1; font-size: .75rem; font-weight: 700; margin-bottom: .2rem;}
    .card {background: #fff; border: 1px solid #E6EBF2; border-radius: 16px;
           padding: 1rem 1.2rem; box-shadow: 0 2px 8px rgba(20,40,80,.05); height: 100%;}
    .card .label {color: #6B7A90; font-size: .8rem; margin-bottom: .2rem;}
    .card .value {font-size: 1.45rem; font-weight: 700; color: #14213D;}
    .card .sub {font-size: .85rem; font-weight: 500; margin-top: .1rem;}
    .card .ttl {font-weight: 700; font-size: .95rem; margin-bottom: .5rem; color: #14213D;}
    .card ul {margin: 0; padding-left: 1.1rem; color: #2B3A55; font-size: .92rem; line-height: 1.8;}
    .pos {border-top: 4px solid #22A06B;} .neg {border-top: 4px solid #F97316;} .wat {border-top: 4px solid #1B4DB1;}
    .pill {display: inline-block; background: #EAF0FD; color: #1B4DB1; border-radius: 999px;
           padding: .25rem .8rem; font-size: .85rem; font-weight: 500; margin: .15rem .2rem .15rem 0;}
    .pill.warn {background: #FFF1E5; color: #C2570C;}
    .mini {display: flex; align-items: center; gap: .7rem;}
    .mini .t1 {font-weight: 700; color: #14213D; font-size: .98rem; line-height: 1.2;}
    .mini .t2 {color: #6B7A90; font-size: .78rem;}
    .chg2 {font-weight: 900; font-size: 1.35rem; margin-top: .6rem;}
    .note {color: #51617A; font-size: .8rem; margin-top: .5rem;}
    .range .bar {position: relative; height: 10px; border-radius: 999px;
                 background: linear-gradient(90deg, #2F6FED 0%, #CBD5E1 50%, #E5484D 100%); margin: 1.1rem 0 .5rem;}
    .range .dot {position: absolute; top: -5px; width: 20px; height: 20px; border-radius: 50%;
                 background: #fff; border: 4px solid #14213D; transform: translateX(-50%);}
    .range .ends {display: flex; justify-content: space-between; color: #6B7A90; font-size: .78rem;}
    .news-row {display: flex; gap: .6rem; align-items: flex-start; padding: .35rem 0; color: #2B3A55;
               font-size: .9rem; line-height: 1.5; border-bottom: 1px solid #F0F3F8;}
    .news-row i {width: 10px; height: 10px; border-radius: 50%; flex: none; margin-top: .45rem;}
    .disclaimer {color: #8793A6; font-size: .8rem; text-align: center; margin-top: 1.5rem;}
    [data-testid="stVerticalBlockBorderWrapper"] {background: #fff; border-radius: 16px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- 데이터 (같은 요청은 캐시해서 무료 한도를 아낀다) ----------
@st.cache_data(ttl=600, show_spinner=False)
def load_data(name):
    kind, ticker = core.resolve(name)
    if kind == "unlisted":  # 주가 데이터가 없는 기업은 위키·뉴스만 모은다
        wiki = core.get_wiki(name)
        news = core.get_news(name, core.UNLISTED_NEWS_COUNT)
        image = core.get_image_uri(wiki["이미지"]) if wiki and wiki.get("이미지") else None
        return {"kind": kind, "wiki": wiki, "news": news, "image": image}
    stock = core.get_stock(ticker)
    news = core.get_news(name if not name.isascii() else stock["회사명"])
    return {"kind": kind, "ticker": ticker, "stock": stock, "news": news, "hist": core.get_history(ticker)}


@st.cache_data(ttl=3600, show_spinner=False)
def load_peers(name):
    names = core.peers_of(name)
    return core.market_snapshot(names) if names else []


@st.cache_data(ttl=3600, show_spinner=False)
def load_analysis(name, stock, news, peers):
    return core.analyze(name, stock, news, peers)


@st.cache_data(ttl=3600, show_spinner=False)
def load_analysis_unlisted(name, wiki, news):
    return core.analyze_unlisted(name, wiki, news)


@st.cache_data(ttl=3600, show_spinner=False)
def load_screen():
    rows = core.market_snapshot(list(core.TICKERS))
    return core.screen_candidates(rows)


@st.cache_data(ttl=86400, show_spinner=False)
def load_logo(ticker):
    return core.get_logo(ticker)


def prefetch_logos(tickers):
    with ThreadPoolExecutor(max_workers=8) as pool:  # 로고를 한꺼번에 받아 대기 시간을 줄인다
        list(pool.map(load_logo, tickers))


# ---------- 화면 조각 ----------
def pct(v):
    if v is None:
        return "정보 없음"
    return "0.00%" if abs(v) < 0.005 else f"{v:+.2f}%"  # -0.00% 같은 표기를 막는다


def color_of(v):
    return UP if (v or 0) >= 0 else DOWN


def card(label, value, sub=None, color=None):
    sub_html = f'<div class="sub" style="color:{color}">{sub}</div>' if sub else ""
    return f'<div class="card"><div class="label">{label}</div><div class="value">{value}</div>{sub_html}</div>'


def logo_html(ticker, name, size=56):
    """로고가 있으면 이미지, 없으면 이름 첫 글자를 넣은 색 원을 보여준다."""
    uri = load_logo(ticker)
    if uri:
        return f'<img class="logo" src="{uri}" width="{size}" height="{size}" style="padding:{size // 8}px">'
    return initial_html(ticker, name, size)


def initial_html(seed, name, size):
    hue = sum(map(ord, seed)) % 360
    return (
        f'<div class="initial" style="width:{size}px;height:{size}px;font-size:{size // 2}px;'
        f'background:hsl({hue},55%,45%)">{escape(name[:1])}</div>'
    )


def summary_banner(text):
    st.markdown(f'<div class="summary"><small>AI 한 줄 요약</small>{escape(text or "정보 없음")}</div>',
                unsafe_allow_html=True)


def list_card(title, items, kind):
    lis = "".join(f"<li>{escape(i)}</li>" for i in (items or [])) or "<li>정보 없음</li>"
    return f'<div class="card {kind}"><div class="ttl">{title}</div><ul>{lis}</ul></div>'


def pills(items, warn=False):
    cls = "pill warn" if warn else "pill"
    return "".join(f'<span class="{cls}">{escape(i)}</span>' for i in (items or [])) or "정보 없음"


def price_chart(hist, color):
    df = pd.DataFrame({"날짜": hist.index.tz_localize(None), "종가": hist.values})
    df["20일 평균"] = df["종가"].rolling(20).mean()
    lo, hi = df["종가"].min(), df["종가"].max()
    pad = (hi - lo) * 0.08
    scale = alt.Scale(domain=[lo - pad, hi + pad], nice=False, zero=False)
    x = alt.X("날짜:T", title=None, axis=alt.Axis(format="%m/%d", grid=False))
    y = alt.Y("종가:Q", title=None, scale=scale)
    area = alt.Chart(df).mark_area(
        clip=True,
        line={"color": color, "strokeWidth": 2},
        color=alt.Gradient(
            gradient="linear",
            stops=[alt.GradientStop(color=color, offset=0), alt.GradientStop(color="white", offset=1)],
            x1=1, x2=1, y1=1, y2=0,
        ),
        opacity=0.25,
    ).encode(x=x, y=y, tooltip=[alt.Tooltip("날짜:T", format="%Y-%m-%d"), alt.Tooltip("종가:Q", format=",.0f")])
    avg = alt.Chart(df).mark_line(color="#8793A6", strokeDash=[4, 3], strokeWidth=1.5, clip=True).encode(
        x=x, y=alt.Y("20일 평균:Q", title=None, scale=scale))
    return (area + avg).properties(height=250).configure_view(stroke=None)


def range_gauge(stock):
    """52주 최저~최고 사이에서 현재가가 어디쯤인지 막대로 보여준다."""
    lo, hi, cur = stock["52주 최저"], stock["52주 최고"], stock["현재가"]
    if not (lo and hi and cur and hi > lo):
        return card("52주 위치", "정보 없음")
    pos = min(max((cur - lo) / (hi - lo) * 100, 0), 100)
    return (
        f'<div class="card range"><div class="label">52주 범위에서의 위치</div>'
        f'<div class="value">{pos:.0f}% 지점</div>'
        f'<div class="bar"><div class="dot" style="left:{pos}%"></div></div>'
        f'<div class="ends"><span>최저 {core.fmt(lo)}</span><span>최고 {core.fmt(hi)}</span></div></div>'
    )


def sentiment_donut(sentiments):
    counts = pd.Series(sentiments or []).value_counts()
    labels = {k: f"{k} {int(counts.get(k, 0))}건" for k in SENT_COLOR}
    df = pd.DataFrame({"분위기": [labels[k] for k in SENT_COLOR], "건수": [int(counts.get(k, 0)) for k in SENT_COLOR]})
    if df["건수"].sum() == 0:
        return None
    return (
        alt.Chart(df).mark_arc(innerRadius=48, outerRadius=80)
        .encode(
            theta="건수:Q",
            color=alt.Color("분위기:N", sort=list(df["분위기"]),
                            scale=alt.Scale(domain=list(df["분위기"]), range=list(SENT_COLOR.values())),
                            legend=alt.Legend(title=None, orient="right", labelFontSize=13)),
            tooltip=["분위기", "건수"],
        )
        .properties(height=180)
    )


def news_list(news, sentiments):
    sentiments = (sentiments or []) + ["중립"] * len(news)
    rows = "".join(
        f'<div class="news-row"><i style="background:{SENT_COLOR.get(s, "#CBD5E1")}"></i>'
        f'<span>{escape(n["title"])}</span></div>'
        for n, s in zip(news, sentiments)
    )
    return f'<div class="card">{rows}</div>'


def news_section(news, sentiments):
    """뉴스 분위기 도넛 차트 + 감성 색 점이 붙은 뉴스 목록."""
    left, right = st.columns([2, 3])
    with left:
        st.markdown("##### 📰 뉴스 분위기")
        donut = sentiment_donut(sentiments)
        if donut is not None:
            st.altair_chart(donut, width="stretch")
    with right:
        st.markdown("##### 최근 뉴스")
        st.markdown(news_list(news, sentiments), unsafe_allow_html=True)


def peer_chart(me, peers, metric):
    rows = [me] + peers
    df = pd.DataFrame({"기업": [r["name"] for r in rows], "값": [r[metric] for r in rows],
                       "본인": [i == 0 for i in range(len(rows))]}).dropna()
    base = alt.Chart(df).encode(
        y=alt.Y("기업:N", sort="-x", title=None),
        x=alt.X("값:Q", title=None, axis=alt.Axis(format="+.0f", grid=True)),
    )
    bars = base.mark_bar(cornerRadius=4, size=22).encode(
        color=alt.condition(alt.datum.값 >= 0, alt.value(UP), alt.value(DOWN)),
        opacity=alt.condition(alt.datum.본인, alt.value(1.0), alt.value(0.55)),
        tooltip=["기업", alt.Tooltip("값:Q", format="+.2f")],
    )
    text = base.mark_text(align="left", dx=4, fontSize=12).encode(text=alt.Text("값:Q", format="+.1f"))
    return (bars + text).properties(height=max(150, 36 * len(df))).configure_view(stroke=None)


def mini_card(row, show="ch3m", note="3개월", comment=None):
    value = row[show]
    price = f"{row['price']:,.0f}원" if row["currency"] == "KRW" else f"${row['price']:,.2f}"
    comment_html = f'<div class="note">{escape(comment)}</div>' if comment else ""
    return (
        f'<div class="card"><div class="mini">{logo_html(row["ticker"], row["name"], 40)}'
        f'<div><div class="t1">{escape(row["name"])}</div><div class="t2">{row["ticker"]}</div></div></div>'
        f'<div class="chg2" style="color:{color_of(value)}">{pct(value)}</div>'
        f'<div class="t2">{note}</div><div class="t2">현재가 {price}</div>{comment_html}</div>'
    )


def mini_grid(rows, show="ch3m", note="3개월", notes=None):
    cols = st.columns(len(rows))
    for col, row in zip(cols, rows):
        col.markdown(mini_card(row, show, note, (notes or {}).get(row["name"])), unsafe_allow_html=True)


def show_raw(analysis):
    """모델이 형식을 못 지켜서 원문만 받은 경우."""
    with st.container(border=True):
        st.markdown(analysis["raw"])


# ---------- 상장 기업 ----------
def render_listed(name, data, analysis, peers):
    ticker, stock, news, hist = data["ticker"], data["stock"], data["news"], data["hist"]
    cur = stock["통화"] or ""
    ch3 = stock["최근 3개월 등락(%)"]
    market = "국내" if ticker.endswith((".KS", ".KQ")) else "해외"
    st.markdown(
        f'<div class="company">{logo_html(ticker, name, 72)}<div>'
        f'<div class="name">{escape(name)}</div>'
        f'<div class="meta"><span class="badge">{market}</span><span class="badge">{ticker}</span>'
        f'{escape(stock["회사명"])} · {escape(stock["업종"] or "업종 정보 없음")}</div></div></div>',
        unsafe_allow_html=True,
    )
    raw = "raw" in analysis
    if not raw:
        summary_banner(analysis.get("summary"))

    cols = st.columns(4)
    price_text = f"{stock['현재가']:,.0f}원" if cur == "KRW" else f"{stock['현재가']:,.2f} {cur}"
    cols[0].markdown(card("현재가", price_text, pct(stock["최근 1주 등락(%)"]) + " (1주)",
                          color_of(stock["최근 1주 등락(%)"])), unsafe_allow_html=True)
    cols[1].markdown(card("3개월 등락", pct(ch3), "1개월 " + pct(stock["최근 1개월 등락(%)"]), color_of(ch3)),
                     unsafe_allow_html=True)
    cols[2].markdown(card("시가총액", core.fmt(stock["시가총액"]),
                          f"PER {core.fmt(stock['PER'])} · PBR {core.fmt(stock['PBR'])}"), unsafe_allow_html=True)
    cols[3].markdown(card("배당수익률", f"{core.fmt(stock['배당수익률(%)'])}%" if stock["배당수익률(%)"] else "정보 없음"),
                     unsafe_allow_html=True)

    st.markdown("&nbsp;")
    left, right = st.columns([3, 2])
    with left:
        st.markdown("##### 📈 최근 6개월 주가 (점선: 20일 평균)")
        st.altair_chart(price_chart(hist, color_of(ch3)), width="stretch")
    with right:
        st.markdown("&nbsp;")
        st.markdown(range_gauge(stock), unsafe_allow_html=True)

    if raw:
        show_raw(analysis)
    else:
        a, b, c = st.columns(3)
        a.markdown(list_card("👍 긍정 요인", analysis.get("positives"), "pos"), unsafe_allow_html=True)
        b.markdown(list_card("⚠️ 위험 요인", analysis.get("risks"), "neg"), unsafe_allow_html=True)
        c.markdown(list_card("🔭 지켜볼 점", analysis.get("watch"), "wat"), unsafe_allow_html=True)

    if peers:
        st.markdown("&nbsp;")
        sectors = " · ".join(core.sector_of(name))
        st.markdown(f"##### 🔎 같은 업종 비교" + (f"  <span class='badge'>{escape(sectors)}</span>" if sectors else ""),
                    unsafe_allow_html=True)
        metric_label = st.radio("비교 기준", ["3개월 등락", "1개월 등락", "52주 고점 대비"], horizontal=True,
                                key=f"metric_{name}", label_visibility="collapsed")
        metric = {"3개월 등락": "ch3m", "1개월 등락": "ch1m", "52주 고점 대비": "from_high"}[metric_label]
        me = {"name": name, "ch1m": stock["최근 1개월 등락(%)"], "ch3m": stock["최근 3개월 등락(%)"],
              "from_high": ((stock["현재가"] / stock["52주 최고"] - 1) * 100) if stock["52주 최고"] else None}
        st.altair_chart(peer_chart(me, peers, metric), width="stretch")
        mini_grid(peers, show=metric, note=metric_label, notes=None if raw else analysis.get("peer_notes"))

    st.markdown("&nbsp;")
    news_section(news, None if raw else analysis.get("news_sentiment"))

    report = core.build_report(name, ticker, stock, news, analysis)
    st.download_button("📄 리포트 내려받기 (.md)", report, file_name=f"{datetime.now():%Y%m%d}_{name}.md",
                       mime="text/markdown", key=f"dl_{name}")


# ---------- 비상장 기업 ----------
def render_unlisted(name, data, analysis):
    wiki, news = data["wiki"], data["news"]
    logo = (
        f'<img class="logo" src="{data["image"]}" width="72" height="72" style="padding:6px">'
        if data["image"] else initial_html(name, name, 72)
    )
    desc = (wiki or {}).get("설명") or "소개 자료를 찾지 못했습니다"
    st.markdown(
        f'<div class="company">{logo}<div><div class="name">{escape(name)}</div>'
        f'<div class="meta"><span class="badge">비상장 · 주가 정보 없음</span>{escape(desc)}</div></div></div>',
        unsafe_allow_html=True,
    )
    raw = "raw" in analysis
    if raw:
        show_raw(analysis)
    else:
        summary_banner(analysis.get("summary"))
        if analysis.get("about"):
            st.markdown(f'<div class="card"><div class="label">어떤 회사인가</div>'
                        f'<div class="value" style="font-size:1.05rem">{escape(analysis["about"])}</div></div>',
                        unsafe_allow_html=True)
            st.markdown("&nbsp;")
        a, b, c = st.columns(3)
        a.markdown(list_card("📌 최근 이슈", analysis.get("issues"), "pos"), unsafe_allow_html=True)
        b.markdown(list_card("⚠️ 위험 요인", analysis.get("risks"), "neg"), unsafe_allow_html=True)
        c.markdown(list_card("🔭 지켜볼 점", analysis.get("watch"), "wat"), unsafe_allow_html=True)
        st.markdown("&nbsp;")
        st.markdown("##### 🔍 직접 확인이 필요한 정보 (주가·재무 데이터 없음)")
        st.markdown(pills(analysis.get("need_check"), warn=True), unsafe_allow_html=True)
        st.caption("상장사인데 이 화면이 나온다면 티커를 직접 입력해 보세요. (예: 035420.KS)")

    st.markdown("&nbsp;")
    news_section(news, None if raw else analysis.get("news_sentiment"))
    if wiki:
        with st.expander("📖 위키백과 회사 소개"):
            st.write(wiki["소개"])
            st.markdown(f"[위키백과에서 보기]({wiki['링크']})")

    report = core.build_report_unlisted(name, wiki, news, analysis)
    st.download_button("📄 리포트 내려받기 (.md)", report, file_name=f"{datetime.now():%Y%m%d}_{name}.md",
                       mime="text/markdown", key=f"dl_{name}")


def run_with_progress(bar, label, start, end, fn, *args, tau=6.0):
    """fn을 다른 스레드에서 돌리는 동안 진행률 막대를 start→end%로 천천히 채운다.
    (끝나는 시점을 알 수 없어서 시간이 갈수록 end에 가까워지게 움직인다)"""
    box = {}

    def target():
        try:
            box["value"] = fn(*args)
        except Exception as e:  # 오류는 메인 스레드에서 다시 던진다
            box["error"] = e

    thread = threading.Thread(target=target)
    add_script_run_ctx(thread, get_script_run_ctx())
    begin = time.time()
    thread.start()
    while thread.is_alive():
        elapsed = time.time() - begin
        pos = start + (end - start) * 0.95 * (1 - math.exp(-elapsed / tau))
        bar.progress(int(pos), text=f"{label}  {int(pos)}%  ({elapsed:.0f}초)")
        time.sleep(0.25)
    bar.progress(end, text=f"{label}  {end}%")
    if "error" in box:
        raise box["error"]
    return box["value"]


def render(name):
    slot = st.empty()  # 진행 상황은 이 자리에만 보이고, 끝나면 사라진다
    with slot.container(), st.status(f"{name} 분석 중...", expanded=True) as status:
        bar = st.progress(0, text="시작합니다  0%")
        data = run_with_progress(bar, "📥 기업 정보 수집 중", 0, 30, load_data, name, tau=4.0)
        peers = []
        if data["kind"] == "unlisted":
            analysis = run_with_progress(bar, f"🤖 {core.HF_MODEL} 분석 중 (주가·재무 정보 없음)", 30, 99,
                                         load_analysis_unlisted, name, data["wiki"], data["news"], tau=10.0)
        else:
            peers = run_with_progress(bar, "🔎 같은 업종 기업 비교 중", 30, 50, load_peers, name, tau=3.0)
            run_with_progress(bar, "🖼️ 회사 로고 불러오는 중", 50, 60, prefetch_logos,
                              [data["ticker"]] + [p["ticker"] for p in peers], tau=2.0)
            analysis = run_with_progress(bar, f"🤖 {core.HF_MODEL} 분석 중", 60, 99,
                                         load_analysis, name, data["stock"], data["news"], peers, tau=10.0)
        bar.progress(100, text="분석 완료  100%")
    slot.empty()

    if data["kind"] == "unlisted":
        render_unlisted(name, data, analysis)
    else:
        render_listed(name, data, analysis, peers)


def rank_row(rank, row, show, note):
    """순위가 붙은 한 줄짜리 기업 카드."""
    value = row[show]
    price = f"{row['price']:,.0f}원" if row["currency"] == "KRW" else f"${row['price']:,.2f}"
    return (
        f'<div class="rank-row"><span class="rank">{rank}</span>{logo_html(row["ticker"], row["name"], 38)}'
        f'<div class="grow"><div class="t1">{escape(row["name"])}</div><div class="t2">{row["ticker"]} · {price}</div></div>'
        f'<div class="chg3" style="color:{color_of(value)}">{pct(value)}<div class="t2">{note}</div></div></div>'
    )


def empty_state(icon, title, desc):
    st.markdown(
        f'<div class="empty"><div class="icon">{icon}</div><div class="etitle">{title}</div>'
        f'<div class="edesc">{desc}</div></div>',
        unsafe_allow_html=True,
    )


def mask_email(addr):
    name, _, domain = (addr or "").partition("@")
    return f"{name[:2]}{'*' * max(len(name) - 2, 1)}@{domain}" if domain else "설정 안 됨"


def show_alert_results(results):
    for info, events, summary in results:
        head = info["name"] + (f" · {info['ticker']}" if info.get("ticker") else " · 비상장")
        rows = []
        for e in events:
            rows.append(f'<div class="ev"><b>{EVENT_EMOJI[e["type"]]} {escape(e["title"])}</b>'
                        + (f'<span class="t2"> {escape(e["detail"])}</span>' if e.get("detail") else "") + "</div>")
            for i in e.get("items", []):
                label = "악재" if i["tag"] == "risk" else "호재"
                rows.append(f'<div class="ev sub"><span class="pill {"warn" if i["tag"] == "risk" else ""}">{label}</span> '
                            f'{escape(i["title"])}</div>')
        summary_html = f'<div class="ai-line">{escape(summary)}</div>' if summary else ""
        st.markdown(f'<div class="card"><div class="ttl">{escape(head)}</div>{summary_html}{"".join(rows)}</div>',
                    unsafe_allow_html=True)


EVENT_EMOJI = {"price": "⚡", "high": "📈", "low": "📉", "news": "📰"}


# ---------- 화면 ----------
st.markdown(
    '<div class="app-head"><div class="app-title">기업 분석 <span>RPA</span></div>'
    '<div class="app-sub">기업명만 고르면 주가·뉴스를 모아 AI가 한눈에 보이도록 정리해 드려요.</div></div>',
    unsafe_allow_html=True,
)

# 주소에 ?names=삼성전자,토스 처럼 적으면 바로 분석된다 (링크로 공유 가능)
url_names = [n.strip() for n in st.query_params.get("names", "").split(",") if n.strip()][:MAX_COMPANIES]
if url_names and "names" not in st.session_state:
    st.session_state.names = url_names

# 같은 회사의 다른 이름(네이버/NAVER 등)은 하나만 보여준다
seen, options = set(), []
for n, t in core.TICKERS.items():
    if t not in seen:
        seen.add(t)
        options.append(n)
options += [n for n in url_names if n not in options]


def tag(n):
    return f"{n}  ·  {'국내' if n in core.KR_TICKERS else '해외' if n in core.US_TICKERS else '직접 입력'}"


QUICK = ["삼성전자", "엔비디아", "현대차", "카카오", "토스"]

if "picked" not in st.session_state:
    st.session_state.picked = url_names or ["삼성전자"]


def add_quick():
    """빠른 선택 칩을 누르면 기업 선택 칸에 추가한다."""
    name = st.session_state.get("quick")
    cur = st.session_state.picked
    if name and name not in cur and len(cur) < MAX_COMPANIES:
        st.session_state.picked = cur + [name]
    st.session_state.quick = None


with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="mark">📊</div><div><div class="bt">기업 분석</div>'
        '<div class="bs">주가·뉴스 자동 리포트</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-label">분석할 기업</div>', unsafe_allow_html=True)
    picked = st.multiselect(
        "기업 선택",
        options=options,
        key="picked",
        format_func=tag,
        accept_new_options=True,
        placeholder="이름 검색 또는 티커 입력",
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div class="hint"><span>{len(picked)}/{MAX_COMPANIES} 선택</span>'
        f'<span>목록에 없으면 이름을 직접 입력</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-label" style="margin-top:1.1rem">빠른 선택</div>', unsafe_allow_html=True)
    st.pills("빠른 선택", QUICK, key="quick", on_change=add_quick, label_visibility="collapsed")
    st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
    if st.button("분석 시작", type="primary", width="stretch", disabled=not picked, icon=":material/play_arrow:"):
        if len(picked) > MAX_COMPANIES:
            st.toast(f"한 번에 {MAX_COMPANIES}개까지만 분석해요. 앞의 {MAX_COMPANIES}개만 진행합니다.", icon="ℹ️")
        # 표시용 꼬리표('  ·  국내' 등)가 붙어 오는 경우를 대비해 이름만 남긴다. (다운로드 등으로 다시 실행돼도 결과가 유지된다)
        st.session_state.names = [n.split("  ·  ")[0].strip() for n in picked[:MAX_COMPANIES]]
    with st.expander("사용 안내", icon=":material/info:"):
        st.markdown(
            "- 상장사는 주가·재무까지, **비상장 기업**은 소개와 뉴스로 분석해요.\n"
            "- 상장사를 이름으로 못 찾으면 티커를 입력하세요. (예: `035420.KS`)\n"
            "- 같은 기업은 잠시 저장된 결과를 보여줘요.\n"
            f"- AI 모델: `{core.HF_MODEL}`"
        )

tab_analysis, tab_screen, tab_alert = st.tabs(["기업 분석", "오늘의 관심 종목", "🔔 알림"])

with tab_analysis:
    names = st.session_state.get("names")
    if names:
        tabs = st.tabs(names) if len(names) > 1 else [st.container()]
        for tab, name in zip(tabs, names):
            with tab:
                try:
                    render(name)
                except Exception as e:  # 한 기업이 실패해도 다른 탭은 보여준다
                    st.error(f"'{name}' 분석에 실패했어요: {e}")
    else:
        empty_state("🔍", "분석할 기업을 골라 주세요", "왼쪽에서 기업을 선택하고 <b>분석 시작</b>을 눌러 보세요.")

with tab_screen:
    if st.session_state.get("screen_on"):
        with st.spinner("전체 기업의 주가를 불러오는 중이에요..."):
            screen = load_screen()
            prefetch_logos([r["ticker"] for r in screen["momentum"] + screen["dip"]])
        left, right = st.columns(2)
        with left:
            st.markdown("##### 🚀 3개월 상승률 상위")
            st.markdown("".join(rank_row(i, r, "ch3m", "3개월") for i, r in enumerate(screen["momentum"], 1)),
                        unsafe_allow_html=True)
        with right:
            st.markdown("##### 🔻 52주 고점 대비 하락 폭 상위")
            st.markdown("".join(rank_row(i, r, "from_high", "고점 대비") for i, r in enumerate(screen["dip"], 1)),
                        unsafe_allow_html=True)
        st.caption("주가 흐름만으로 단순 선별한 관심 후보예요. 재무·전망은 반영하지 않으며, 상승·반등을 보장하지 않습니다.")
    else:
        empty_state("⭐", "관심 가져볼 만한 종목 찾기",
                    f"등록된 {len(options)}개 기업을 주가 흐름만으로 훑어서<br>상승률이 높은 기업과 고점에서 많이 내려온 기업을 보여드려요.")
        _, mid, _ = st.columns([2, 1.4, 2])
        if mid.button("관심 종목 불러오기", type="primary", width="stretch"):
            st.session_state.screen_on = True
            st.rerun()

with tab_alert:
    settings = core.load_settings()
    if not core.mail_ready():
        empty_state("🔔", "메일 알림을 켜려면 설정이 필요해요",
                    "<code>.env</code>에 <code>MAIL_FROM</code>(보내는 Gmail), <code>MAIL_APP_PASSWORD</code>(구글 앱 비밀번호), "
                    "<code>MAIL_TO</code>(받는 주소)를 채우고 다시 실행해 주세요.")
    else:
        st.markdown(
            f'<div class="card"><div class="label">알림 받을 주소</div>'
            f'<div class="value" style="font-size:1.1rem">{escape(mask_email(os.getenv("MAIL_TO")))}</div>'
            f'<div class="note">주가가 크게 움직이거나, 52주 신고가·신저가에 닿거나, 악재·호재 키워드가 든 새 뉴스가 나오면 메일로 알려드려요.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("&nbsp;")
        watch = st.multiselect("감시할 기업", options=options, format_func=tag, accept_new_options=True,
                               default=[n for n in settings["companies"] if n in options]
                               or [n.split("  ·  ")[0].strip() for n in picked if n.split("  ·  ")[0].strip() in options],
                               placeholder="알림을 받을 기업을 골라 주세요")
        threshold = st.slider("주가 급변 기준 (전일 대비 ±%)", 1.0, 10.0, float(settings["threshold"]), 0.5)
        c1, c2, c3 = st.columns(3)
        watch_names = [n.split("  ·  ")[0].strip() for n in watch]
        if c1.button("설정 저장", width="stretch", disabled=not watch_names):
            core.save_settings(watch_names, threshold)
            st.toast("저장했어요. 터미널에서 --watch로 실행하면 이 설정을 써요.", icon="✅")
        if c2.button("지금 점검하고 알림받기", type="primary", width="stretch", disabled=not watch_names):
            if time.time() - st.session_state.get("last_check", 0) < 30:
                st.toast("방금 점검했어요. 잠시 후 다시 눌러 주세요.", icon="⏳")
            else:
                st.session_state.last_check = time.time()
                with st.spinner("기업을 점검하는 중이에요..."):
                    results, sent = core.run_alerts(watch_names, threshold)
                st.session_state.alert_view = (results, sent, bool(watch_names))
        if c3.button("테스트 메일 보내기", width="stretch"):
            core.send_mail("[기업 알림] 테스트 메일", "알림 메일이 정상적으로 설정됐어요.",
                           '<div style="font-family:sans-serif;padding:16px">✅ 알림 메일이 정상적으로 설정됐어요.</div>')
            st.toast("테스트 메일을 보냈어요.", icon="📧")

        view = st.session_state.get("alert_view")
        if view:
            results, sent, _ = view
            st.markdown("&nbsp;")
            if results:
                st.success("변화를 찾아서 메일을 보냈어요." if sent else "변화를 찾았어요.")
                show_alert_results(results)
            else:
                st.info("지금은 알릴 변화가 없어요. 처음 점검한 기업은 기준만 저장하고, 다음 점검부터 변화를 알려드려요.")

        with st.expander("자동으로 계속 점검하려면"):
            st.markdown(
                "웹 화면을 열어 두지 않아도 터미널에서 주기적으로 점검할 수 있어요. 위에서 **설정 저장**을 먼저 눌러 주세요."
            )
            st.code("python 261020_bucheon_hugging_jbs.py --watch 30     # 30분마다 점검 (Ctrl+C로 종료)\n"
                    "python 261020_bucheon_hugging_jbs.py --once         # 한 번만 점검 (작업 스케줄러용)", language="bash")

st.markdown(
    '<div class="disclaimer">AI와 공개 데이터를 이용한 참고 자료이며 투자 권유가 아니에요. 투자 판단과 책임은 본인에게 있습니다.</div>',
    unsafe_allow_html=True,
)
