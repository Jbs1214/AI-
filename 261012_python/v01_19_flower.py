from termcolor import colored

# 꽃잎, 꽃술, 줄기, 잎 모양
petal = [
    "   @@@   ",
    " @@@@@@@ ",
    "@@@ ",       # 꽃술 왼쪽 꽃잎
    " @@@@@@@ ",
    "   @@@   ",
]

def draw_flower(petal_color="magenta"):
    print(colored(petal[0], petal_color))
    print(colored(petal[1], petal_color))
    # 가운데 줄: 꽃잎 + 노란 꽃술 + 꽃잎
    print(colored(petal[2], petal_color) + colored("*", "yellow", attrs=["bold"]) + colored(" @@@", petal_color))
    print(colored(petal[3], petal_color))
    print(colored(petal[4], petal_color))

    # 줄기와 잎
    stem = [
        "    |    ",
        "  \\ |    ",
        "   \\|/   ",
        "    |    ",
    ]
    for line in stem:
        print(colored(line, "green"))


for color in ["magenta", "red", "cyan"]:
    draw_flower(color)
    print()
