from ecc.controller.base_controller import BaseController
from ecc.types import VariableType, ConstantType, Bit


class GateController(BaseController):
    def __init__(self) -> None:
        super().__init__()

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
        """add bias toward zero"""
        self._add_variable(in0, 1)

    def get_zero_bit(self) -> Bit:
        """create a new bit and add bias to zero"""
        zero = self.get_bit()
        self.zero_gate(zero)
        return zero

    def one_gate(self, in0: Bit) -> None:
        """add bias toward one"""
        self._add_variable(in0, -1)
        self._add_offset(1)

    def get_one_bit(self) -> Bit:
        """create a new bit and add bias to one"""
        one = self.get_bit()
        self.one_gate(one)
        return one

    def not_gate(self, in0: Bit, out: Bit) -> None:
        """not gate"""
        # add the variables (in order)
        self._add_variable(in0, -1)
        self._add_variable(out, -1)

        # add the quadratic biases
        self._add_quadratic(in0, out, 2)

        self._add_offset(1)

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
        A: VariableType,
        B: VariableType,
        ctrl: Bit,
        C: VariableType,
    ) -> None:
        """A if ctrl is 0 B if ctrl is 1"""
        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        out = self.check_VariableType(C)

        if len(a) == len(b) == len(out):
            pass
        else:
            raise ValueError(
                "length of variable1, variable2, output should be same")

        for i in range(len(a)):
            self.ctrl_select(a[i], b[i], ctrl, out[i])

    def ctrl_var(
        self, ctrl: Bit, A: VariableType, C: VariableType
    ) -> None:
        """Returns var if control is 1, else returns 0"""
        a = self.check_VariableType(A)
        c = self.check_VariableType(C)

        if len(a) != len(c):
            raise ValueError("var and out Variable length is not same")

        for i in range(len(a)):
            self.and_gate(a[i], ctrl, c[i])
