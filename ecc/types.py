from typing import Union
import numpy as np

Bit = int
Binary = Union[int, np.int8]  # dimod returns solver's result as np.int8
Name = int
Variable = list[Bit]
Constant = Union[int, list[Binary]]
