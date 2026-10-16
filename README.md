# YOLO 이미지 분류 챌린지 — 표정 분류 모델 직접 만들기

**Happy · Sad · Normal** 3가지 표정을 분류하는 나만의 모델을 **내 손으로** 학습합니다.
코드·데이터셋·폴더는 전부 직접 만듭니다. 이 폴더에는 정답 코드가 없고, 안내와 코치만 있습니다.

```
미리 학습된 yolo11n-cls.pt → 내 표정 데이터로 미세 조정(Fine-tuning) → best.pt
   train 학습  →  val 검증  →  test 최종 확인
```

## 진행 순서

| 단계 | 문서 | 내가 만드는 것 |
|---|---|---|
| 0 | `guide/00_큰그림.md` | (읽기) 전체 흐름 이해 |
| 1 | `guide/01_데이터셋_직접_만들기.md` | `dataset/` 폴더 (train·val·test × 3클래스) |
| 2 | `guide/02_학습_코드_직접_작성.md` | `train.py` (본인 작성) |
| 3 | `guide/03_결과_해석.md` | 결과 해석 메모 |
| 4 | `guide/04_미션_제출.md` | GitHub 업로드 + 링크 공유 |
| 막힘 | `guide/05_막혔을때.md` · `guide/06_공식문서_링크.md` | — |

## 환경 (로컬 Anaconda)

```
conda activate py311
pip install ultralytics
```

## 코치와 같이 하기

| 방법 | 사용 |
|---|---|
| Claude Code | 이 폴더에서 `claude` 실행 → 자동으로 `Learning` 스타일 + 계획 모드. `yolo-cls-coach` 에이전트에게 질문 |
| 일반 AI 채팅 | `AGENT_PROMPT.md` 내용을 첫 메시지에 붙여넣기 |

코치는 정답 코드를 바로 주지 않습니다. 힌트 → 내가 작성 → 리뷰 순서로 진행됩니다.

## 폴더 지도

```
make_cls_yolo_model/
├─ README.md · CLAUDE.md · AGENT_PROMPT.md
├─ .claude/ (settings.json · agents/yolo-cls-coach.md)
└─ guide/ (00 ~ 06)
```
