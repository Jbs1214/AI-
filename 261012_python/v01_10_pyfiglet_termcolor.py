import pyfiglet
from termcolor import colored

sentence = "Hello"
py_text = pyfiglet.figlet_format(sentence)
color_text = colored(py_text, "yellow", "on_red", ["bold"])
print(color_text)