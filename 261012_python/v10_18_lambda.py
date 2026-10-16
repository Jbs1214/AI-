add = lambda a, b : a+b

print(add(10, 13))

# pyfiglet 기본 함수
import pyfiglet
def decorate_text(text):
    return pyfiglet.figlet_format(text)

decorate = lambda text : pyfiglet.figlet_format(text)

print(decorate("HELLO"))