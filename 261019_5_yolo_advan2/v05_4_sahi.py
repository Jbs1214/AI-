from sahi.utils.file import download_from_url

# 작은 차량 이미지 (멀리서 찍은 도로)
download_from_url(
    "https://raw.githubusercontent.com/obss/sahi/main/demo/demo_data/small-vehicles1.jpeg",
    "demo_data/small-vehicles1.jpeg",
)

# 항공 촬영 지형 이미지
download_from_url(
    "https://raw.githubusercontent.com/obss/sahi/main/demo/demo_data/terrain2.png",
    "demo_data/terrain2.png",
)

print("이미지 다운로드 완료")