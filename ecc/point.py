from ecc.types import Variable, Constant


class Point:
    def __init__(self, x: Variable, y: Variable):
        if len(x) != len(y):
            raise ValueError('Length of x and y is different')

        self.length = len(x)
        self._x = x
        self._y = y

    @property
    def x(self) -> Variable:
        return self._x

    @property
    def y(self) -> Variable:
        return self._y


class PointConst:
    def __init__(self, x: Constant, y: Constant):
        if len(x) != len(y):
            raise ValueError('Length of x and y is different')

        self.length = len(x)
        self._x = x
        self._y = y

    @property
    def x(self) -> Constant:
        return self._x

    @property
    def y(self) -> Constant:
        return self._y
