from typing import Union
import warnings
import numpy as np

from dwave.system import DWaveSampler, EmbeddingComposite
from dimod.binary import BinaryQuadraticModel
from dimod.vartypes import Vartype
from dimod import ExactSolver
from dimod.sampleset import SampleView, SampleSet

from ecc.utilities import number_to_binary
from ecc.types import VariableType, ConstantType, Bit


class BaseController:
    def __init__(self) -> None:
        self.bqm = BinaryQuadraticModel(Vartype.BINARY)

        self.bit_cnt = 0
        self.variables: dict[str, list[Bit]] = {}
        self.constants: dict[str, int] = {}

        self.dwave_sampler = None
        self.embedding_sampler = None

    def get_sampler(self):
        self.dwave_sampler = DWaveSampler()
        print("QPU {} was selected.".format(self.dwave_sampler.solver.name))

        self.embedding_sampler = EmbeddingComposite(self.dwave_sampler)

    def run_DWaveSampler(self, num_reads: int = 100, label: str = 'controller') -> SampleSet:
        if not self.embedding_sampler:
            self.get_sampler()

        solution = self.embedding_sampler.sample(
            self.bqm, num_reads=num_reads, label=label)

        return solution

    def run_ExactSolver(self) -> SampleSet:
        solver = ExactSolver()
        solution = solver.sample(self.bqm)

        return solution

    def create_variable(self, name: str, length: int) -> list[Bit]:
        if self.exists_variable(name):
            raise ValueError("Variable already exists")

        self.variables[name] = self.get_bits(length)
        return self.get_variable(name)

    def get_variable(self, name: str) -> list[Bit]:
        if v := self.variables.get(name):
            return v

        raise ValueError("Unknown variable name")

    def exists_variable(self, name: str) -> bool:
        if self.variables.get(name):
            return True

        return False

    def check_VariableType(self, variable: VariableType) -> list[Bit]:
        var = self.get_variable(variable) if isinstance(
            variable, str) else variable
        return var

    def check_ConstantType(self, constant: ConstantType, length=None) -> list[int]:
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

    def get_bit(self) -> Bit:
        """create and returns a new Bit"""
        bit = Bit(self.bit_cnt)
        self.bit_cnt += 1
        return bit

    def get_bits(self, num: int) -> list[Bit]:
        """create and returns list of new Bits"""
        bits = [self.get_bit() for _ in range(num)]
        return bits

    def extract_bit(self, sample: SampleView, bit: Bit) -> int:
        if not isinstance(sample, SampleView):
            sample = sample.sample

        result = None
        try:
            result = sample[bit.index]
        except Exception as e:
            if (c := self.constants.get(bit.index)) != None:
                result = c

            warnings.warn(f"Value for {bit.index} was not found")

        return result

    def extract_variable(self, sample: SampleView, variable: VariableType) -> list[int]:
        """extract value of variable in sample"""
        var = self.check_VariableType(variable)

        if not isinstance(sample, SampleView):
            sample = sample.sample

        result = [None for _ in var]
        for i in range(len(var)):
            try:
                result[i] = sample[var[i].index]
            except Exception as e:
                if (c := self.constants.get(var[i].index)) != None:
                    result[i] = c
                    continue

                warnings.warn(f"Value for {i} was not found")

        return result

    def set_variable_constant(
        self, variable: VariableType, value: ConstantType
    ) -> None:
        var = self.check_VariableType(variable)
        value = self.check_ConstantType(value, len(var))

        for i in range(len(var)):
            self.set_bit_constant(var[i], value[i])

    def set_bit_constant(self, bit: Union[Bit, str], value: int) -> None:
        bit_name: str = bit.index if isinstance(bit, Bit) else bit

        try:
            self.bqm.fix_variable(bit_name, value)
        except ValueError as e:
            print(f"Warning - {e}")

        self.constants[bit_name] = value

    def get_shape(self) -> int:
        return self.bqm.shape

    def _add_variable(self, bit: Bit, bias: int = 0) -> None:
        self.bqm.add_variable(bit.index, bias)

    def _add_quadratic(self, bit1: Bit, bit2: Bit, bias: int) -> None:
        self.bqm.add_quadratic(bit1.index, bit2.index, bias)

    def _flip_variable(self, bit: Bit) -> None:
        self.bqm.flip_variable(bit.index)

    def _add_offset(self, v: int):
        self.bqm.offset += v

    def merge_bit(self, bit1: Bit, bit2: Bit) -> None:
        """merge bit1 to bit2"""
        for u, bias in self.bqm.iter_neighborhood(bit1.index):
            self.bqm.add_quadratic(bit2.index, u, bias)

        linear = self.bqm.get_linear(bit1.index)
        self._add_variable(bit2, linear)
        self.bqm.remove_variable(bit1.index)
        bit1.index = bit2.index
