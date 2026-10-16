user_input = input("값을 입력해주세요 :")
print("입력한 값은 : ", user_input)

try:
    meters = float(user_input)
    feet = meters * 3.28084
    print(f"{meters} 미터는 {feet} 피트입니다.")

except ValueError:
    print("숫자를 입력해야 합니다. 입력한 값은 숫자가 아닙니다.")