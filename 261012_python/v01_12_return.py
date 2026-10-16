import pyfiglet
from termcolor import colored

def make_highlight(text:str) :

    py_text = pyfiglet.figlet_format(text)
    color_py_text = colored(py_text, "red")
    return color_py_text

print(make_highlight("Hello"))