# 파일 쓰기
with open("memo.txt", "w", encoding = "utf-8") as f :
    f.write("새로운 한 줄 추가")

print("쓰기 완료")

# 파일 읽기
with open("memo.txt", "r", encoding= "utf-8") as f :
    text = f.read()
    print(text)

print("읽기 완료")

# 파일 이어 쓰기
with open("memo.txt", "a", encoding= "utf-8") as f :
    f.write("\n이어 쓰기")

print("이어쓰기 완료")

