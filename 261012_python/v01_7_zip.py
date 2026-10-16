names = ["뽀삐", "초코", "쿠키"]
scores = [95, 88, 72]

for name, score in zip(names, scores) :
    print(f"{name} : {score}점")


pairs = dict(zip(names, scores))
print(pairs)

