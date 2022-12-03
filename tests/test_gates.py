import ecc
import unittest
from parameterized import parameterized

from tests import base


class TestGateController(base.Base):
    def setUp(self) -> None:
        self.controller = ecc.GateController()

    @parameterized.expand([(0, 0, 0, 0), (0, 1, 1, 0), (1, 0, 1, 0), (1, 1, 0, 1)])
    def test_halfadder_gate(self, in0: int, in1: int, sum_: int, carry: int):
        a, b, c, d = self.controller.get_bits(4)

        self.controller.halfadder_gate(a, b, c, d)

        self.check_change(a, b, c, d)

        self.controller.set_bit_constant(a, in0)
        self.controller.set_bit_constant(b, in1)

        self.check_solution((c, sum_), (d, carry))

    @parameterized.expand([(0, 0, 0, 0, 0), (0, 0, 1, 1, 0), (0, 1, 0, 1, 0), (0, 1, 1, 0, 1), (1, 0, 0, 1, 0), (1, 0, 1, 0, 1), (1, 1, 0, 0, 1), (1, 1, 1, 1, 1)])
    def test_fulladder_gate(self, in0: int, in1: int, in2: int, sum_: int, carry: int):
        a, b, c, d, e = self.controller.get_bits(5)

        self.controller.fulladder_gate(a, b, c, d, e)

        self.check_change(a, b, c, d, e)

        self.controller.set_bit_constant(a, in0)
        self.controller.set_bit_constant(b, in1)
        self.controller.set_bit_constant(c, in2)

        self.check_solution((d, sum_), (e, carry))

    def test_zero_gate(self):
        a = self.controller.get_bit()

        self.controller.zero_gate(a)

        self.check_change(a)

        self.check_solution((a, 0))

    def test_get_zero_bit(self):
        a = self.controller.get_zero_bit()

        self.check_change(a)

        self.check_solution((a, 0))

    @parameterized.expand([(0, 1), (1, 0)])
    def test_not_gate(self, in0: int, out: int):
        a = self.controller.get_bit()
        c = self.controller.get_bit()

        self.controller.not_gate(a, c)

        self.check_change(a, c)

        self.controller.set_bit_constant(a, in0)

        self.check_solution((c, out))

    @parameterized.expand([(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)])
    def test_and_gate(self, in0: int, in1: int, out: int):
        a, b, c = self.controller.get_bits(3)

        self.controller.and_gate(a, b, c)

        self.check_change(a, b, c)

        self.controller.set_bit_constant(a, in0)
        self.controller.set_bit_constant(b, in1)

        self.check_solution((c, out))

    @parameterized.expand([(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)])
    def test_or_gate(self, in0: int, in1: int, out: int):
        a = self.controller.get_bit()
        b = self.controller.get_bit()
        c = self.controller.get_bit()

        self.controller.or_gate(a, b, c)

        self.check_change(a, b, c)

        self.controller.set_bit_constant(a, in0)
        self.controller.set_bit_constant(b, in1)

        self.check_solution((c, out))

    @parameterized.expand([(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)])
    def test_xor_gate(self, in0: int, in1: int, out: int):
        a = self.controller.get_bit()
        b = self.controller.get_bit()
        c = self.controller.get_bit()

        self.controller.xor_gate(a, b, c)

        self.check_change(a, b, c)

        self.controller.set_bit_constant(a, in0)
        self.controller.set_bit_constant(b, in1)

        self.check_solution((c, out))

    @parameterized.expand([(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)])
    def test_xnor_gate(self, in0: int, in1: int, out: int):
        a = self.controller.get_bit()
        b = self.controller.get_bit()
        c = self.controller.get_bit()

        self.controller.xnor_gate(a, b, c)

        self.check_change(a, b, c)

        self.controller.set_bit_constant(a, in0)
        self.controller.set_bit_constant(b, in1)

        self.check_solution((c, out))

    @parameterized.expand([(0, 0, 0, 0), (0, 1, 0, 0), (1, 0, 0, 1), (1, 1, 0, 1), (0, 0, 1, 0), (0, 1, 1, 1), (1, 0, 1, 0), (1, 1, 1, 1)])
    def test_ctrl_select(self, in0: int, in1: int, control: int, out: int):
        a = self.controller.get_bit()
        b = self.controller.get_bit()
        ctrl = self.controller.get_bit()
        c = self.controller.get_bit()

        self.controller.ctrl_select(a, b, ctrl, c)

        self.check_change(a, b, c)

        self.controller.set_bit_constant(a, in0)
        self.controller.set_bit_constant(b, in1)
        self.controller.set_bit_constant(ctrl, control)

        self.check_solution((c, out))

    @parameterized.expand([(2, 6, 1, 6)])
    def test_ctrl_select_variable(self, A, B, control, C):
        a = self.controller.get_bits(3)
        b = self.controller.get_bits(3)
        c = self.controller.get_bits(3)
        ctrl = self.controller.get_bit()

        self.controller.ctrl_select_variable(a, b, ctrl, c)

        self.check_change(a, b, c, ctrl)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)
        self.controller.set_bit_constant(ctrl, control)

        self.check_solution((c, C))

    @parameterized.expand([(1, 6, 6), (0, 6, 0)])
    def test_ctrl_var(self, control, A, C):
        a = self.controller.get_bits(3)
        c = self.controller.get_bits(3)
        ctrl = self.controller.get_bit()

        self.controller.ctrl_var(ctrl, a, c)

        self.check_change(a, c, ctrl)

        self.controller.set_variable_constant(a, A)
        self.controller.set_bit_constant(ctrl, control)

        self.check_solution((c, C))


if __name__ == "__main__":
    unittest.main()
