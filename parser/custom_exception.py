

class NoneException(Exception):
    def __init__(self):
        self.msg = "Данный продукт не в наличии"

    def __str__(self):
        return self.msg