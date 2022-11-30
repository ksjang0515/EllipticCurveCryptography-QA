from typing import Union
import warnings

from dwave.system import DWaveSampler, EmbeddingComposite
from dimod.binary import BinaryQuadraticModel
from dimod.vartypes import Vartype
from dimod import ExactSolver
from dimod.sampleset import SampleView, SampleSet

from ecc.utilities import number_to_binary
from ecc.bit import Bit


"""TODO - Create type for single bit
make bit type to be passed by reference so modification can be made"""
VariableType = Union[str, list[Bit]]
ConstantType = Union[int, list[int]]


"""TODO - Create a method for getting graph of bqm"""
"""TODO - Make sure set_variable is done at the end
because dimod removes the variable when using fix_variable"""


class Controller:
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

    def run_DWaveSampler(self, num_reads=100, label='controller') -> SampleSet:
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
        bit = Bit(self.bit_cnt)
        self.bit_cnt += 1
        return bit

    def get_bits(self, num: int) -> list[Bit]:
        bits = [self.get_bit() for _ in range(num)]
        return bits

    def get_zero_bit(self) -> Bit:
        zero = self.get_bit()
        self.zero_gate(zero)
        return zero

    def extract_variable(self, sample: SampleView, variable: VariableType) -> list[int]:
        """TODO - Add type for parameter sample, dimod.sampleset.Sample"""
        var = self.check_VariableType(variable)

        result = [None for _ in var]
        for i in range(len(var)):
            try:
                result[i] = (
                    sample[var[i].index]
                    if isinstance(sample, SampleView)
                    else sample.sample[var[i].index]
                )
            except Exception as e:
                if c := self.constants.get(var[i].index):
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

    def _add_variable(self, bit: Bit, bias: int = 0) -> None:
        self.bqm.add_variable(bit.index, bias)

    def _add_quadratic(self, bit1: Bit, bit2: Bit, bias: int) -> None:
        self.bqm.add_quadratic(bit1.index, bit2.index, bias)

    def _flip_variable(self, bit: Bit) -> None:
        self.bqm.flip_variable(bit.index)

    def halfadder_gate(self, in0: Bit, in1: Bit, sum_: Bit, carry: Bit) -> None:
        """halfadder gate"""
        # add the variables (in order)
        self._add_variable(in0, 1)
        self._add_variable(in1, 1)
        self._add_variable(sum_, 1)
        self._add_variable(carry, 4)

        # add the quadratic biases
        self._add_quadratic(in0, in1, 2)
        self._add_quadratic(in0, sum_, -2)
        self._add_quadratic(in0, carry, -4)
        self._add_quadratic(in1, sum_, -2)
        self._add_quadratic(in1, carry, -4)
        self._add_quadratic(sum_, carry, 4)

    def fulladder_gate(
        self, in0: Bit, in1: Bit, in2: Bit, sum_: Bit, carry: Bit
    ) -> None:
        """fulladder gate"""
        # add the variables (in order)
        self._add_variable(in0, 1)
        self._add_variable(in1, 1)
        self._add_variable(in2, 1)
        self._add_variable(sum_, 1)
        self._add_variable(carry, 4)

        # add the quadratic biases
        self._add_quadratic(in0, in1, 2)
        self._add_quadratic(in0, in2, 2)
        self._add_quadratic(in0, sum_, -2)
        self._add_quadratic(in0, carry, -4)
        self._add_quadratic(in1, in2, 2)
        self._add_quadratic(in1, sum_, -2)
        self._add_quadratic(in1, carry, -4)
        self._add_quadratic(in2, sum_, -2)
        self._add_quadratic(in2, carry, -4)
        self._add_quadratic(sum_, carry, 4)

    def zero_gate(self, in0: Bit) -> None:
        """zero gate, make bit to result in zero"""
        self._add_variable(in0, 1)

    def not_gate(self, in0: Bit, out: Bit) -> None:
        """not gate"""
        # add the variables (in order)
        self._add_variable(in0, -1)
        self._add_variable(out, -1)

        # add the quadratic biases
        self._add_quadratic(in0, out, 2)

    def and_gate(self, in0: Bit, in1: Bit, out: Bit) -> None:
        """and gate"""
        # add the variables (in order)
        self._add_variable(in0)
        self._add_variable(in1)
        self._add_variable(out, 3)

        # add the quadratic biases
        self._add_quadratic(in0, in1, 1)
        self._add_quadratic(in0, out, -2)
        self._add_quadratic(in1, out, -2)

    def or_gate(self, in0: Bit, in1: Bit, out: Bit) -> None:
        """or gate"""
        # add the variables (in order)
        self._add_variable(in0, 1)
        self._add_variable(in1, 1)
        self._add_variable(out, 1)

        # add the quadratic biases
        self._add_quadratic(in0, in1, 1)
        self._add_quadratic(in0, out, -2)
        self._add_quadratic(in1, out, -2)

    def xor_gate(self, in0: Bit, in1: Bit, out: Bit) -> None:
        """xor gate"""
        ancilla = self.get_bit()

        # add the variables (in order)
        self._add_variable(in0, 1)
        self._add_variable(in1, 1)
        self._add_variable(out, 1)
        self._add_variable(ancilla, 4)

        # add the quadratic biases
        self._add_quadratic(in0, in1, 2)
        self._add_quadratic(in0, out, -2)
        self._add_quadratic(in1, out, -2)
        self._add_quadratic(in0, ancilla, -4)
        self._add_quadratic(in1, ancilla, -4)
        self._add_quadratic(ancilla, out, 4)

    def xnor_gate(self, in0: Bit, in1: Bit, out: Bit) -> None:
        self.xor_gate(in0, in1, out)
        self._flip_variable(out)

    def ctrl_select(self, in0: Bit, in1: Bit, ctrl: Bit, out: Bit) -> None:
        """in0 if ctrl is 0, in1 if ctrl is 1"""
        ancilla = self.get_bit()

        self._add_variable(in0, 1)
        self._add_variable(in1)
        self._add_variable(ctrl)
        self._add_variable(out, 3)
        self._add_variable(ancilla, 8)

        self._add_quadratic(in0, in1, 2)
        self._add_quadratic(in0, ctrl, -1)
        self._add_quadratic(in1, ctrl, 1)
        self._add_quadratic(in0, out, -4)
        self._add_quadratic(in1, out, -2)
        self._add_quadratic(ctrl, out, 2)
        self._add_quadratic(in0, ancilla, 2)
        self._add_quadratic(in1, ancilla, -4)
        self._add_quadratic(ctrl, ancilla, -4)
        self._add_quadratic(out, ancilla, -4)

    def ctrl_select_variable(
        self,
        variable1: VariableType,
        variable2: VariableType,
        ctrl: Bit,
        output: VariableType,
    ) -> None:
        """variable1 if ctrl is 0 variable2 if ctrl is 1"""
        var1 = self.check_VariableType(variable1)
        var2 = self.check_VariableType(variable2)
        out = self.check_VariableType(output)

        if len(var1) == len(var2) == len(out):
            pass
        else:
            raise ValueError(
                "length of variable1, variable2, output should be same")

        for i in range(len(var1)):
            self.ctrl_select(var1[i], var2[i], ctrl, out[i])

    def ctrl_var(
        self, control: Bit, variable: VariableType, output: VariableType
    ) -> None:
        """Returns var if control is 1, else returns 0"""
        var = self.check_VariableType(variable)
        out = self.check_VariableType(output)

        if len(var) != len(out):
            raise ValueError("var and out Variable length is not same")

        for i in range(len(var)):
            self.and_gate(var[i], control, out[i])

    def add(
        self, A: VariableType, B: VariableType, C: VariableType
    ) -> None:
        """C = A + B"""
        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        if not len(c) == max(len(a), len(b)) + 1:
            raise ValueError("out Variable length is too short")

        if len(a) < len(b):
            # swap so var1 is longer than var2
            temp = a
            a = b
            b = temp

        carry = self.get_bit()
        self.halfadder_gate(a[0], b[0], c[0], carry)

        for i in range(1, len(b)):
            pre_carry = carry
            carry = self.get_bit()
            self.fulladder_gate(a[i], b[i], pre_carry, c[i], carry)

        if len(a) == len(b):
            c[-1].index = carry.index
            return

        for i in range(len(b), len(a)):
            pre_carry = carry
            carry = self.get_bit()
            self.halfadder_gate(a[i], pre_carry, c[i], carry)
        c[-1].index = carry.index

    def add_no_overflow(
        self, A: VariableType, B: VariableType, C: VariableType
    ) -> None:
        """C = A + B (no last carry)"""
        """TODO - remove carry in last operation"""
        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        if not len(c) == max(len(a), len(b)):
            raise ValueError("out Variable length is too short")

        if len(a) < len(b):
            # swap so var1 is longer than var2
            temp = a
            a = b
            b = temp

        carry = self.get_bit()
        self.halfadder_gate(a[0], b[0], c[0], carry)

        for i in range(1, len(b)):
            pre_carry = carry
            carry = self.get_bit()
            self.fulladder_gate(a[i], b[i], pre_carry, c[i], carry)

        if len(a) == len(b):
            return

        for i in range(len(b), len(a)):
            pre_carry = carry
            carry = self.get_bit()
            self.halfadder_gate(a[i], pre_carry, c[i], carry)

    def add_const(
        self, A: VariableType, B: ConstantType, C: VariableType
    ) -> None:
        """C = A + B"""

        """requires less bit if B is power of 2, but if B is odd number
        this requires more bits than using add method because xor uses one ancilla bit"""

        warnings.warn(
            "add_const method is less efficient than plain add method if constant is odd number")

        a = self.check_VariableType(A)
        b = self.check_ConstantType(B)
        c = self.check_VariableType(C)

        if len(a) < len(b):
            raise ValueError("constant cannot be longer than variable")

        if not len(c) == len(a) + 1:
            raise ValueError("out Variable length is too short")

        carry = None
        for i in range(len(b)):
            if carry:
                pre_carry = carry
                carry = self.get_bit()
                sum_ = self.get_bit()

                if b[i] == 1:
                    self.xnor_gate(a[i], pre_carry, sum_)
                    self.or_gate(a[i], pre_carry, carry)

                else:
                    self.xor_gate(a[i], pre_carry, sum_)
                    self.and_gate(a[i], pre_carry, carry)
            else:
                if b[i] == 1:
                    sum_ = self.get_bit()
                    carry = a[i]

                    self.not_gate(a[i], sum_)

                else:
                    sum_ = a[i]

            c[i].index = sum_.index

        if len(a) == len(carry):
            c[-1].index = carry.index
            return

        if not carry:
            for i in range(len(b), len(a)):
                c[i].index = a[i].index

            zero = self.get_bit()
            self.zero_gate(zero)
            c[-1].index = zero.index

            return

        for i in range(len(b), len(a)):
            pre_carry = carry
            carry = self.get_bit()
            sum_ = self.get_bit()

            self.halfadder_gate(a[i], pre_carry, sum_, carry)

            c[i].index = sum_.index

        c[-1].index = carry.index

    def subtract(
        self,
        A: VariableType,
        B: VariableType,
        C: VariableType,
        underflow: Bit,
    ):
        """C = A - B"""
        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        if not (len(c) == len(a) == len(b)):
            raise ValueError(
                "variable1, variable2, output length must be same")

        var_ = [*a, underflow]

        self.add(b, c, var_)

    def multiply(
        self, A: VariableType, B: VariableType, C: VariableType
    ) -> None:
        """C = A * B"""
        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        var1_length = len(a)  # n
        var2_length = len(b)  # n2
        out_length = len(c)

        if (
            var1_length + var2_length != out_length
            and var1_length * var2_length
            != out_length  # case where one of variables' length is one
        ):
            raise ValueError("out Variable length is too short")

        ctrl_ancilla_var = self.get_bits(var1_length)
        self.ctrl_var(b[0], a, ctrl_ancilla_var)

        pre_add_ancilla_var = ctrl_ancilla_var[1:]  # n-1
        c[0].index = ctrl_ancilla_var[0].index

        for i in range(1, var2_length):
            ctrl_ancilla_var = self.get_bits(var1_length)  # n
            self.ctrl_var(b[i], a, ctrl_ancilla_var)

            # n+1 (n+n => n+1 or n-1+n => n+1)
            add_ancilla_var = self.get_bits(var1_length + 1)
            self.add(pre_add_ancilla_var, ctrl_ancilla_var, add_ancilla_var)

            pre_add_ancilla_var = add_ancilla_var[1:]  # n
            c[i].index = add_ancilla_var[0].index

        # (n + n2) - n2 = n
        for i in range(len(pre_add_ancilla_var)):
            c[var2_length + i].index = pre_add_ancilla_var[i].index

    def multiply_const(
        self, A: VariableType, B: ConstantType, C: VariableType
    ) -> None:
        """Unlike add_const method, multiply_const requires less bits because this doesn't use any xor_gate"""
        a = self.check_VariableType(A)
        b = self.check_ConstantType(B)
        c = self.check_VariableType(C)

        var_length = len(a)
        const_length = len(b)

        if var_length + const_length != len(c) and var_length * const_length == len(
            c
        ):
            raise ValueError("out Variable length is too short")

        pre_add_ancilla_var = []
        for i in range(const_length):
            if pre_add_ancilla_var:
                if b[i] == 1:
                    add_ancilla_var = self.get_bits(var_length + 1)
                    self.add(a, pre_add_ancilla_var, add_ancilla_var)
                    c[i].index = add_ancilla_var[0].index
                    pre_add_ancilla_var = add_ancilla_var[1:]

                else:
                    c[i].index = pre_add_ancilla_var[0].index
                    pre_add_ancilla_var = pre_add_ancilla_var[1:]

            else:
                if b[i] == 1:
                    ctrl_ancilla_var = a[:]
                    c[i].index = ctrl_ancilla_var[0].index
                    pre_add_ancilla_var = ctrl_ancilla_var[1:]

                else:
                    c[i].index = self.get_zero_bit().index

        for i in range(len(pre_add_ancilla_var)):
            c[const_length + i].index = pre_add_ancilla_var[i].index

        current = const_length + len(pre_add_ancilla_var)
        if current == len(c):
            return

        for i in range(current, len(c)):
            c[i].index = self.get_zero_bit().index

    def square(self, A: VariableType, C: VariableType) -> None:
        def ctrl_skip_var(var, index, out):
            for i in range(len(var)):
                if i == index:
                    out[i].index = var[i].index
                    continue

                self.and_gate(var[i], var[index], out[i])

        a = self.check_VariableType(A)
        c = self.check_VariableType(C)

        var_length = len(a)  # n

        if 2 * var_length != len(c):
            raise ValueError("out Variable length is too short")

        ctrl_ancilla_var = self.get_bits(var_length)
        ctrl_skip_var(a, 0, ctrl_ancilla_var)

        pre_add_ancilla_var = ctrl_ancilla_var[1:]  # n-1
        c[0].index = ctrl_ancilla_var[0].index

        for i in range(1, var_length):
            ctrl_ancilla_var = self.get_bits(var_length)  # n
            ctrl_skip_var(a, i, ctrl_ancilla_var)

            # n+1 (n+n => n+1 or n-1+n => n+1)
            add_ancilla_var = self.get_bits(var_length + 1)
            self.add(pre_add_ancilla_var, ctrl_ancilla_var, add_ancilla_var)

            pre_add_ancilla_var = add_ancilla_var[1:]  # n
            c[i].index = add_ancilla_var[0].index

        # (n + n2) - n2 = n
        for i in range(len(pre_add_ancilla_var)):
            c[var_length + i].index = pre_add_ancilla_var[i].index
