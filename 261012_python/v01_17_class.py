class Hotdog:
    BASE_PRICE = 2000
    SIZE_MULTIPLIER = {"소": 1, "중": 2, "대": 3}

    def __init__(self, sauce, size, bread):
        if size not in self.SIZE_MULTIPLIER:
            raise ValueError(
                f"해당 사이즈는 없습니다: '{size}' ('소', '중', '대' 중 하나를 입력해주세요)"
            )
        self.sauce = sauce
        self.size = size
        self.bread = bread

    def make(self):
        print(f"{self.bread}빵을 사용한 {self.sauce} 핫도그를 만듭니다. 사이즈는 '{self.size}'입니다.")

    def price(self):
        return self.BASE_PRICE * self.SIZE_MULTIPLIER[self.size]


orders = [
    ("칠리", "소", "기본"),
    ("데리야끼", "대", "플랫"),
    ("데리야끼", "특대", "플랫"),
]

for sauce, size, bread in orders:
    try:
        h = Hotdog(sauce, size, bread)
    except ValueError as e:
        print(e)
        print("-" * 30)
        continue

    h.make()
    print(f"{h.price()}원 입니다.")
    print("-" * 30)