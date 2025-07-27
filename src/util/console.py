from termcolor import colored

class Console: 

    def info(self, message: str):
        self.log(message, "white")

    def success(self, message: str):
        self.log(message, "green")

    def warning(self, message: str):
        self.log(message, "yellow")

    def error(self, message: str):
        self.log(message, "red")

    def log(self, message: str, color: str = "white"):
        print(colored(message, color))