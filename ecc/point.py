from ecc.types import Variable, Constant
from ecc.utilities.number_to_binary import number_to_binary


class Point:
    def __init__(self, x: Variable, y: Variable):
        if len(x) != len(y):
            raise ValueError('Length of x and y is different')

        self.length = len(x)
        self.x = x
        self.y = y


class PointConst:
    def __init__(self, x: int, y: int, length: int = 256):
        self.length = length
        self.x: Constant = number_to_binary(x, length)
        self.y: Constant = number_to_binary(y, length)
        self.x_int = x
        self.y_int = y
