from typing import Union
import warnings

from dimod.sampleset import SampleView


from ecc.types import ConstantType
from ecc.controller.base_controller import BaseController
from ecc.utilities import number_to_binary


class BitController(BaseController):
    def __init__(self) -> None:
        self.bit_cnt = 0
        self.bit_to_name: dict[int, int] = {}  # bit -> name
        self.name_to_bit: dict[int, list[int]] = {}  # name -> bits

        self.constants: dict[int, int] = {}  # bit -> binary

        super().__init__()

    def check_ConstantType(self, constant: ConstantType, length=None) -> list[int]:
        """returns list of ints for given constant"""
        const = (
            number_to_binary(constant, length)
            if isinstance(constant, int)
            else constant
        )

        if length and len(const) != length:
            raise ValueError(
                "length of given constant is not same as given length")

        if not len(const):
            raise ValueError("length of constant is 0")

        return const

    def get_bit(self) -> int:
        """create and returns a bit"""
        bit = self.bit_cnt
        self.bit_cnt += 1

        self.bit_to_name[bit] = bit
        self.name_to_bit[bit] = [bit]

        return bit

    def get_bits(self, num: int) -> list[int]:
        """create and returns list of bits"""
        bits = [self.get_bit() for _ in range(num)]
        return bits

    def get_name(self, *args: list[int]) -> Union[list[int], int]:
        """returns name of given bits, if one bit is given this will return a single int"""
        r = []
        for bit in args:
            if (n := self.bit_to_name[bit]) == None:
                raise ValueError('bit name not found')

            r.append(n)

        if len(r) == 1:
            r = r[0]

        return r

    def get_constant(self, name: int) -> Union[int, None]:
        """returns constant value stored in dictionary for given name"""
        if (c := self.constants.get(name)) == None:
            warnings.warn(f"Value for {name} was not found")

        return c

    def extract_bit(self, sample: SampleView, bit: int) -> int:
        """returns value of given bit in sample, if not present it tries to search on constants"""
        if not isinstance(sample, SampleView):
            sample = sample.sample

        name = self.get_name(bit)

        if (result := sample.get(name)) != None:
            return result

        return self.get_constant(name)

    def extract_variable(self, sample: SampleView, bits: list[int]) -> list[int]:
        """returns value of given bits in sample, if not present it tries to search on constants"""

        if not isinstance(sample, SampleView):
            sample = sample.sample

        result = [None for _ in bits]
        for i, bit in enumerate(bits):
            name = self.get_name(bit)

            if (r := sample.get(name)) == None:
                r = self.get_constant(name)

            result[i] = r

        return result

    def set_bit_constant(self, bit: int, value: int) -> None:
        """temporarily stores bit value on constants dictionary, will be applied before running solver"""
        self.constants[bit] = value

    def set_variable_constant(self, var: list[int], const: ConstantType) -> None:
        const = self.check_ConstantType(const, len(var))

        for i in range(len(var)):
            self.set_bit_constant(var[i], const[i])

    def merge_bit(self, bit1: int, bit2: int) -> None:
        """merge bit2 to bit1"""
        bit1_name, bit2_name = self.get_name(bit1, bit2)

        bit2_list = self.name_to_bit[bit2_name]
        for bit in bit2_list:
            self.bit_to_name[bit] = bit1_name

        self.name_to_bit[bit1_name] += bit2_list
        self.name_to_bit[bit2_name] = []

        try:
            linear = self.bqm.get_linear(bit2_name)
        except ValueError:
            return

        for u, bias in self.bqm.iter_neighborhood(bit2_name):
            self.bqm.add_quadratic(bit1_name, u, bias)

        self._add_variable(bit1_name, linear)
        self.bqm.remove_variable(bit2_name)

    def merge_variable(self, bits1: list[int], bits2: list[int]) -> None:
        """merge bits2 to bits1"""

        if len(bits1) != len(bits2):
            raise ValueError('Length is not same')

        for bit1, bit2 in zip(bits1, bits2):
            self.merge_bit(bit1, bit2)

    def _set_constant(self):
        """ran before running solver to apply stored constants"""
        for key, value in self.constants.items():
            self._fix_variable(key, value)

    def run_DWaveSampler(self, *args):
        self._set_constant()

        return super().run_DWaveSampler(*args)

    def run_ExactSolver(self, *args):
        self._set_constant()

        return super().run_ExactSolver(*args)

    def _fix_variable(self, bit, value):
        bit_name = self.get_name(bit)
        super()._fix_variable(bit_name, value)

    def _add_variable(self, bit, bias: int = 0) -> None:
        bit_name = self.get_name(bit)
        super()._add_variable(bit_name, bias)

    def _add_quadratic(self, bit1, bit2, bias: int) -> None:
        bit1_name, bit2_name = self.get_name(bit1, bit2)
        super()._add_quadratic(bit1_name, bit2_name, bias)

    def _flip_variable(self, bit) -> None:
        bit_name = self.get_name(bit)
        super()._flip_variable(bit_name)
