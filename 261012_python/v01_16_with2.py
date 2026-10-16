# 이미지 복사
with open("original.jpg", "rb") as src:
    data = src.read()  
    print(data)        # bytes 타입으로 읽힘

with open("copy.png", "wb") as dst:
    dst.write(data)

print("복사 완료:", len(data), "bytes")