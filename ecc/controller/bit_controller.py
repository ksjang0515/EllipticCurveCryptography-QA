from typing import Union, Optional
import warnings

from dimod.sampleset import SampleView
from dimod.sampleset import SampleSet


from ecc.types import Constant, Variable, Bit, Name, Binary
from ecc.controller.base_controller import BaseController
from ecc.utilities.number_to_binary import number_to_binary


class BitController(BaseController):
    def __init__(self) -> None:
        self.bit_cnt = 0
        self.bit_to_name: dict[Bit, Name] = {}
        self.name_to_bit: dict[Name, list[Bit]] = {}

        self.constants: dict[Bit, Binary] = {}
        self.constants_from_name: dict[Name, Binary] = {}

        super().__init__()

    def check_ConstantType(self, constant: Constant, length=None) -> list[Binary]:
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

    def get_bit(self, num: int = None) -> Union[Variable, Bit]:
        """create and returns Bit/Variable"""
        if num == None:
            bit = self.bit_cnt
            self.bit_cnt += 1

            self.bit_to_name[bit] = bit
            self.name_to_bit[bit] = [bit]

        else:
            bit: Variable = [self.get_bit() for _ in range(num)]

        return bit

    def get_bits(self, *args: int) -> list[Variable]:
        """create list of variables"""
        r = []
        for num in args:
            bits = self.get_bit(num)
            r.append(bits)

        return r

    def get_name(self, bit: Union[Variable, Bit]) -> Union[list[Name], Name]:
        """returns name of given bits"""
        if isinstance(bit, list):
            n = self.get_names(*bit)

        elif (n := self.bit_to_name[bit]) == None:
            raise ValueError('bit name not found')

        return n

    def get_names(self, *args: Union[Variable, Bit]) -> list[Union[list[Name], Name]]:
        """returns name of given bits, if one bit is given this will return a single int"""
        r = []
        for bit in args:
            n = self.get_name(bit)
            r.append(n)

        return r

    def get_constant_from_name(self, name: Name) -> Optional[Binary]:
        """returns constant value stored in dictionary for given name, returns None instead of raising error for easier debugging"""
        if (c := self.constants_from_name.get(name)) == None:
            warnings.warn(f"Value for {name} was not found")

        return c

    def _extract_bit(self, sample: SampleView, bit: Bit) -> Optional[Binary]:
        name = self.get_name(bit)

        try:
            # SampleView raises ValueError when using get
            result = sample.get(name)
        except ValueError:
            return self.get_constant_from_name(name)

        return result

    def extract_bit(self, sample: SampleView, bit: Bit) -> Optional[Binary]:
        """returns value of given bit in sample, if not present it tries to search on constants"""
        sample = self.check_Sample(sample)

        return self._extract_bit(sample, bit)

    def _extract_variable(self, sample: SampleView, var: Variable) -> list[Optional[Binary]]:
        result = []
        for bit in var:
            r = self._extract_bit(sample, bit)
            result.append(r)

        return result

    def extract_variable(self, sample: SampleView, var: Variable) -> list[Optional[Binary]]:
        """returns value of given bits in sample, if not present it tries to search on constants"""
        sample = self.check_Sample(sample)

        return self._extract_variable(sample, var)

    def extract(self, sample, *args: Union[Bit, Variable]) -> list[Union[Optional[Binary], list[Optional[Binary]]]]:
        sample = self.check_Sample(sample)

        result = []
        for b in args:
            if isinstance(b, Bit):
                r = self._extract_bit(sample, b)
            else:
                r = self._extract_variable(sample, b)

            result.append(r)

        return result

    def check_Sample(self, sample: SampleView):
        if not isinstance(sample, SampleView):
            return sample.sample

        return sample

    def set_bit_constant(self, bit: Bit, value: Binary) -> None:
        """temporarily stores bit value on constants dictionary, will be applied before running solver"""
        self.constants[bit] = value

    def set_variable_constant(self, var: Variable, const: Constant) -> None:
        const = self.check_ConstantType(const, len(var))

        for i in range(len(var)):
            self.set_bit_constant(var[i], const[i])

    def merge_bit(self, bit1: Bit, bit2: Bit) -> None:
        """merge bit2 to bit1"""
        bit1_name, bit2_name = self.get_names(bit1, bit2)

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

    def merge_variable(self, var1: Variable, var2: Variable) -> None:
        """merge var2 to var1"""

        if len(var1) != len(var2):
            raise ValueError('Length is not same')

        for bit1, bit2 in zip(var1, var2):
            self.merge_bit(bit1, bit2)

    def _set_constant(self) -> None:
        """ran before running solver to apply stored constants"""
        for key, value in self.constants.items():
            bit_name = self.get_name(key)
            self._fix_variable_by_name(bit_name, value)
            self.constants_from_name[bit_name] = value

    def run_DWaveSampler(self, *args) -> SampleSet:
        self._set_constant()

        return super().run_DWaveSampler(*args)

    def run_ExactSolver(self, *args) -> SampleSet:
        self._set_constant()

        return super().run_ExactSolver(*args)

    def _fix_variable(self, bit: Bit, value: Binary):
        bit_name = self.get_name(bit)
        super()._fix_variable_by_name(bit_name, value)

    def _fix_variable_by_name(self, bit_name: Name, value: Binary):
        try:
            super()._fix_variable(bit_name, value)
        except ValueError:
            pass

    def _add_variable(self, bit: Bit, bias: int = 0) -> None:
        bit_name = self.get_name(bit)
        super()._add_variable(bit_name, bias)

    def _add_quadratic(self, bit1: Bit, bit2: Bit, bias: int) -> None:
        bit1_name, bit2_name = self.get_names(bit1, bit2)
        super()._add_quadratic(bit1_name, bit2_name, bias)

    def _flip_variable(self, bit: Bit) -> None:
        bit_name = self.get_name(bit)
        super()._flip_variable(bit_name)
