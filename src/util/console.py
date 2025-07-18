from termcolor import colored

from util.constant import GitoyMessage

class Console: 

    def __init__(self):
        pass

    def info(self, message: GitoyMessage | str):
        self.log(message, "white")

    def success(self, message: GitoyMessage | str):
        self.log(message, "green")

    def warning(self, message: GitoyMessage | str):
        self.log(message, "yellow")

    def error(self, message: GitoyMessage | str):
        self.log(message, "red")

    def log(self, message: GitoyMessage | str, color: str = "white"):
        if isinstance(message, GitoyMessage):
            print(colored(message.value, color))
        else:
            print(colored(message, color))