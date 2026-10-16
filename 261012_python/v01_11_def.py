import pyfiglet
from termcolor import colored
# sentence = "Hello"
# py_sentence = pyfiglet.figlet_format(sentence)
# print(py_sentence)

def good_sentence(sentence : str) :
    """
    입력된 문자를 pyfiglet 형식으로 출력
    매개 변수 : sentence (str)
    반환 : None - 출력만 수행
    """
    py_sentence = pyfiglet.figlet_format(sentence)
    tr_sentence = colored(py_sentence, "black", "on_green", ["bold"] )
    print(tr_sentence)

good_sentence("Happy")