from termcolor import colored

from util.constant import GitoyMessage

class Console: 

    def __init__(self):
        pass

    def info(self, message: GitoyMessage):
            print(message.value)

    def error(self, message: GitoyMessage):
        print(colored(message.value, "red"))