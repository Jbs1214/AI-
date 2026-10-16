"""train ↔ val/test 사이에 '비슷한 사진'이 섞였는지 지각 해시(pHash)로 점검한다.

사전 준비: pip install imagehash pillow
실행: python check_leak.py
"""
from pathlib import Path

import imagehash
from PIL import Image

ROOT = Path("dataset")
CLASSES = ["Happy", "Sad", "Normal"]


def hash_folder(split):
    """split 폴더의 모든 이미지 -> {파일경로: pHash} 딕셔너리."""
    hashes = {}
    for cls in CLASSES:
        for img_path in (ROOT / split / cls).glob("*.jpg"):
            hashes[img_path] = imagehash.phash(Image.open(img_path))
    return hashes


def find_leaks(hashes_a, hashes_b, threshold):
    """a 와 b 의 모든 쌍을 비교해 '비슷한 쌍'을 (파일a, 파일b, 거리) 리스트로 돌려준다.

    imagehash 해시끼리 빼기(h1 - h2) 하면 해밍 거리(다른 비트 수)가 나온다.
    """
    leaks = []
    for path_a, hash_a in hashes_a.items():
        for path_b, hash_b in hashes_b.items():
            dist = hash_a - hash_b
            if dist <= threshold:
                leaks.append((path_a, path_b, dist))
    return leaks


if __name__ == "__main__":
    THRESHOLD = 8  # 임시값: 이 숫자가 맞는지 아래 결과를 보고 직접 판단해 볼 것

    train = hash_folder("train")
    for other in ["val", "test"]:
        leaks = find_leaks(train, hash_folder(other), THRESHOLD)
        print(f"[train ↔ {other}] 비슷한 쌍: {len(leaks)}개")
        for a, b, dist in sorted(leaks, key=lambda x: x[2]):
            print(f"  거리 {dist:2d}  {a.name}  <->  {b.name}")
