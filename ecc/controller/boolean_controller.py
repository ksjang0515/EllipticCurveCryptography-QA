from ecc.controller.base_controller import BaseController
from ecc.types import VariableType, ConstantType, Bit


class BoolController(BaseController):
    def __init__(self) -> None:
        super().__init__()

    def get_zero_bit(self) -> Bit:
        """create a new bit and add bias to zero"""
        zero = self.get_bit()
        self.zero_gate(zero)
        return zero

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
