def meters_to_feet(meters : float) -> float:
    """
    미터를 피트로 환산
    """
    return meters * 3.28084

while True:
    user_input = input("값을 입력해주세요 (종료하려면 'q'를 입력하세요): ")

    if user_input == 'q':
        print("프로그램을 종료합니다.")
        break

    try:
        meters = float(user_input)
        feet = meters_to_feet(meters)
        print(f"{meters} 미터는 {feet} 피트입니다.")
    except ValueError:
        print("숫자를 입력해야 합니다. 입력한 값은 숫자가 아닙니다.")
