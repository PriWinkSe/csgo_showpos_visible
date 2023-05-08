#自定义异常 出错时候打印行号
import inspect

class PosRunTimeError(Exception):
    def __init__(self, message):
        self.message = message
        self.line_number = inspect.currentframe().f_back.f_lineno
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (line {self.line_number})"