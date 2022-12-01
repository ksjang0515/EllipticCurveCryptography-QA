from ecc.bit import Bit


class Point:
    def __init__(self, x: list[Bit], y: list[Bit]):
        self._x = x
        self._y = y

    @property
    def x(self) -> list[Bit]:
        return self._x

    @x.setter
    def x(self, value) -> None:
        self._x = value

    @property
    def y(self) -> list[Bit]:
        return self._y

    @y.setter
    def y(self, value) -> None:
        self._y = value
