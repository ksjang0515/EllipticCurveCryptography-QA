from typing import Union


class Bit:
    def __init__(self, index: Union[int, str]):
        self._index: str = index if isinstance(index, str) else str(index)
        self.changed: bool = False

    @property
    def index(self) -> str:
        return self._index

    @index.setter
    def index(self, value) -> None:
        self._index = value
        self.changed = True

    def __repr__(self):
        return self._index
