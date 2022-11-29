from typing import Union
import os
import warnings

from dimod.binary import BinaryQuadraticModel
from dimod.vartypes import Vartype
from dimod import ExactSolver
from dimod.sampleset import SampleView

from utilities import number_to_binary
from bit import Bit



"""TODO - Create type for single bit
make bit type to be passed by reference so modification can be made"""
VariableType = Union[str, list[Bit]]
ConstantType = Union[int, list[int]]


"""TODO - Create a method for getting graph of bqm"""
"""TODO - Make sure set_variable is done at the end
because dimod removes the variable when using fix_variable"""


class Controller:
    def __init__(self) -> None:
        self.api_key = os.getenv("API_TOKEN")
        if not self.api_key:
            warnings.warn("api key was not found")

        self.bqm = BinaryQuadraticModel(Vartype.BINARY)

        self.bit_cnt = 0
        self.variables: dict[str, list[Bit]] = {}
        self.constants: dict[str, int] = {}

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
        var = self.get_variable(variable) if isinstance(variable, str) else variable
        return var

    def check_ConstantType(self, constant: ConstantType, length=None) -> list[int]:
        const = (
            number_to_binary(constant, length)
            if isinstance(constant, int)
            else constant
        )

        if length and len(const) != length:
            raise ValueError("length of given constant is not same as given length")

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

    def run_ExactSolver(self):
        solver = ExactSolver()
        solution = solver.sample(self.bqm)

        return solution

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
        self._add_variable(in0, 1)

    def not_gate(self, in0: Bit, out: Bit) -> None:
        # add the variables (in order)
        self._add_variable(in0, -1)
        self._add_variable(out, -1)

        # add the quadratic biases
        self._add_quadratic(in0, out, 2)

    def and_gate(self, in0: Bit, in1: Bit, out: Bit) -> None:
        # add the variables (in order)
        self._add_variable(in0)
        self._add_variable(in1)
        self._add_variable(out, 3)

        # add the quadratic biases
        self._add_quadratic(in0, in1, 1)
        self._add_quadratic(in0, out, -2)
        self._add_quadratic(in1, out, -2)

    def or_gate(self, in0: Bit, in1: Bit, out: Bit) -> None:
        # add the variables (in order)
        self._add_variable(in0, 1)
        self._add_variable(in1, 1)
        self._add_variable(out, 1)

        # add the quadratic biases
        self._add_quadratic(in0, in1, 1)
        self._add_quadratic(in0, out, -2)
        self._add_quadratic(in1, out, -2)

    def xor_gate(self, in0: Bit, in1: Bit, out: Bit) -> None:
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
            raise ValueError("length of variable1, variable2, output should be same")

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
        self, variable1: VariableType, variable2: VariableType, output: VariableType
    ) -> None:
        """TODO - allow out variable length to be longer"""
        var1 = self.check_VariableType(variable1)
        var2 = self.check_VariableType(variable2)
        out = self.check_VariableType(output)

        if not len(out) == max(len(var1), len(var2)) + 1:
            raise ValueError("out Variable length is too short")

        if len(var1) < len(var2):
            # swap so var1 is longer than var2
            temp = var1
            var1 = var2
            var2 = temp

        carry = self.get_bit()
        self.halfadder_gate(var1[0], var2[0], out[0], carry)

        for i in range(1, len(var2)):
            pre_carry = carry
            carry = self.get_bit()
            self.fulladder_gate(var1[i], var2[i], pre_carry, out[i], carry)

        if len(var1) == len(var2):
            out[-1].index = carry.index
            return

        for i in range(len(var2), len(var1)):
            pre_carry = carry
            carry = self.get_bit()
            self.halfadder_gate(var1[i], pre_carry, out[i], carry)
        out[-1].index = carry.index

    def add_no_overflow(
        self, variable1: VariableType, variable2: VariableType, output: VariableType
    ) -> None:
        """TODO - remove carry in last operation"""
        var1 = self.check_VariableType(variable1)
        var2 = self.check_VariableType(variable2)
        out = self.check_VariableType(output)

        if not len(out) == max(len(var1), len(var2)):
            raise ValueError("out Variable length is too short")

        if len(var1) < len(var2):
            # swap so var1 is longer than var2
            temp = var1
            var1 = var2
            var2 = temp

        carry = self.get_bit()
        self.halfadder_gate(var1[0], var2[0], out[0], carry)

        for i in range(1, len(var2)):
            pre_carry = carry
            carry = self.get_bit()
            self.fulladder_gate(var1[i], var2[i], pre_carry, out[i], carry)

        if len(var1) == len(var2):
            return

        for i in range(len(var2), len(var1)):
            pre_carry = carry
            carry = self.get_bit()
            self.halfadder_gate(var1[i], pre_carry, out[i], carry)

    def add_const(
        self, variable: VariableType, constant: list[int], output: VariableType
    ) -> None:
        """TODO - allow out variable length to be longer
        requires less bit if constant is power of 2, but if constant is odd number
        this requires more bits than using add method because xor uses one ancilla bit"""

        warnings.warn("add_const method is less efficient if constant is odd number")

        var = self.check_VariableType(variable)
        const = constant
        out = self.check_VariableType(output)

        if len(var) < len(const):
            raise ValueError("constant cannot be longer than variable")

        if not len(out) == len(var) + 1:
            raise ValueError("out Variable length is too short")

        carry = None
        for i in range(len(const)):
            if carry:
                pre_carry = carry
                carry = self.get_bit()
                sum_ = self.get_bit()

                if const[i] == 1:
                    self.xnor_gate(var[i], pre_carry, sum_)
                    self.or_gate(var[i], pre_carry, carry)

                else:
                    self.xor_gate(var[i], pre_carry, sum_)
                    self.and_gate(var[i], pre_carry, carry)
            else:
                if const[i] == 1:
                    sum_ = self.get_bit()
                    carry = var[i]

                    self.not_gate(var[i], sum_)

                else:
                    sum_ = var[i]

            out[i].index = sum_.index

        if len(var) == len(carry):
            out[-1].index = carry.index
            return

        if not carry:
            for i in range(len(const), len(var)):
                out[i].index = var[i].index

            zero = self.get_bit()
            self.zero_gate(zero)
            out[-1].index = zero.index

            return

        for i in range(len(const), len(var)):
            pre_carry = carry
            carry = self.get_bit()
            sum_ = self.get_bit()

            self.halfadder_gate(var[i], pre_carry, sum_, carry)

            out[i].index = sum_.index

        out[-1].index = carry.index

    def subtract(
        self,
        variable1: VariableType,
        variable2: VariableType,
        output: VariableType,
        underflow: Bit,
    ):
        var1 = self.check_VariableType(variable1)
        var2 = self.check_VariableType(variable2)
        out = self.check_VariableType(output)

        if not (len(out) == len(var1) == len(var2)):
            raise ValueError("variable1, variable2, output length must be same")

        var_ = [*var1, underflow]

        self.add(var2, out, var_)

    def multiply(
        self, variable1: VariableType, variable2: VariableType, output: VariableType
    ) -> None:
        var1 = self.check_VariableType(variable1)
        var2 = self.check_VariableType(variable2)
        out = self.check_VariableType(output)

        var1_length = len(var1)  # n
        var2_length = len(var2)  # n2
        out_length = len(out)

        if (
            var1_length + var2_length != out_length
            and var1_length * var2_length
            != out_length  # case where one of variables' length is one
        ):
            raise ValueError("out Variable length is too short")

        ctrl_ancilla_var = self.get_bits(var1_length)
        self.ctrl_var(var2[0], var1, ctrl_ancilla_var)

        pre_add_ancilla_var = ctrl_ancilla_var[1:]  # n-1
        out[0].index = ctrl_ancilla_var[0].index

        for i in range(1, var2_length):
            ctrl_ancilla_var = self.get_bits(var1_length)  # n
            self.ctrl_var(var2[i], var1, ctrl_ancilla_var)

            # n+1 (n+n => n+1 or n-1+n => n+1)
            add_ancilla_var = self.get_bits(var1_length + 1)
            self.add(pre_add_ancilla_var, ctrl_ancilla_var, add_ancilla_var)

            pre_add_ancilla_var = add_ancilla_var[1:]  # n
            out[i].index = add_ancilla_var[0].index

        # (n + n2) - n2 = n
        for i in range(len(pre_add_ancilla_var)):
            out[var2_length + i].index = pre_add_ancilla_var[i].index

    def multiply_const(
        self, variable: VariableType, constant: list[int], output: VariableType
    ) -> None:
        """Unlike add_const method, multiply_const requires less bits because this doesn't use any xor_gate"""
        var = self.check_VariableType(variable)
        const = constant
        out = self.check_VariableType(output)

        var_length = len(var)
        const_length = len(const)

        if var_length + const_length != len(out) and var_length * const_length == len(
            out
        ):
            raise ValueError("out Variable length is too short")

        pre_add_ancilla_var = []
        for i in range(const_length):
            if pre_add_ancilla_var:
                if const[i] == 1:
                    add_ancilla_var = self.get_bits(var_length + 1)
                    self.add(var, pre_add_ancilla_var, add_ancilla_var)
                    out[i].index = add_ancilla_var[0].index
                    pre_add_ancilla_var = add_ancilla_var[1:]

                else:
                    out[i].index = pre_add_ancilla_var[0].index
                    pre_add_ancilla_var = pre_add_ancilla_var[1:]

            else:
                if const[i] == 1:
                    ctrl_ancilla_var = var[:]
                    out[i].index = ctrl_ancilla_var[0].index
                    pre_add_ancilla_var = ctrl_ancilla_var[1:]

                else:
                    out[i].index = self.get_zero_bit().index

        for i in range(len(pre_add_ancilla_var)):
            out[const_length + i].index = pre_add_ancilla_var[i].index

        current = const_length + len(pre_add_ancilla_var)
        if current == len(out):
            return

        for i in range(current, len(out)):
            out[i].index = self.get_zero_bit().index

    def square(self, variable: VariableType, output: VariableType) -> None:
        def ctrl_skip_var(var, index, out):
            for i in range(len(var)):
                if i == index:
                    out[i].index = var[i].index
                    continue

                self.and_gate(var[i], var[index], out[i])

        var = self.check_VariableType(variable)
        out = self.check_VariableType(output)

        var_length = len(var)  # n

        if 2 * var_length != len(out):
            raise ValueError("out Variable length is too short")

        ctrl_ancilla_var = self.get_bits(var_length)
        ctrl_skip_var(var, 0, ctrl_ancilla_var)

        pre_add_ancilla_var = ctrl_ancilla_var[1:]  # n-1
        out[0].index = ctrl_ancilla_var[0].index

        for i in range(1, var_length):
            ctrl_ancilla_var = self.get_bits(var_length)  # n
            ctrl_skip_var(var, i, ctrl_ancilla_var)

            # n+1 (n+n => n+1 or n-1+n => n+1)
            add_ancilla_var = self.get_bits(var_length + 1)
            self.add(pre_add_ancilla_var, ctrl_ancilla_var, add_ancilla_var)

            pre_add_ancilla_var = add_ancilla_var[1:]  # n
            out[i].index = add_ancilla_var[0].index

        # (n + n2) - n2 = n
        for i in range(len(pre_add_ancilla_var)):
            out[var_length + i].index = pre_add_ancilla_var[i].index

    def modulo_p(self, a: VariableType, r: VariableType, P: int, ensure_modulo=False):
        """calculates a = m*P + r
        if ensure_modulo is False result r could be larger than P"""

        p_const = number_to_binary(P)
        p_length = len(p_const)
        a_length = len(a)

        if a_length < p_length:
            raise ValueError("P is too large")
        if len(r) != p_length:
            raise ValueError("r length should be same as P length")

        m_length = a_length - p_length if a_length != p_length else 1
        m = self.get_bits(m_length)
        ancilla_mult = self.get_bits(a_length)

        self.multiply_const(m, p_const, ancilla_mult)
        self.add_no_overflow(ancilla_mult, r, a)

        if ensure_modulo:
            ancilla_add = self.get_bits(p_length)
            p = self.get_bits(p_length)
            underflow = self.get_bit()

            self.subtract(p, r, ancilla_add, underflow)
            self.zero_gate(underflow)

            self.set_variable_constant(p, p_const)
