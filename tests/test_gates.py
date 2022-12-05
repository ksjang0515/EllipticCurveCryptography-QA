import ecc
import unittest
from parameterized import parameterized

from tests import base


class TestGateController(base.Base):
    def setUp(self) -> None:
        self.controller = ecc.GateController()

    def test_halfadder_gate(self):
        a, b, c, d = self.controller.get_bit(4)

        self.controller.halfadder_gate(a, b, c, d)

        result = self.get_result(a, b, c, d)
        answer = set(('0000', '1010', '0110', '1101'))

        self.assertEqual(result, answer)

    def test_fulladder_gate(self):
        a, b, c, d, e = self.controller.get_bit(5)

        self.controller.fulladder_gate(a, b, c, d, e)

        result = self.get_result(a, b, c, d, e)
        answer = set(('00000', '00110', '01010', '01101',
                     '10010', '10101', '11001', '11111'))

        self.assertEqual(result, answer)

    def test_not_gate(self):
        a, c = self.controller.get_bit(2)

        self.controller.not_gate(a, c)

        result = self.get_result(a, c)
        answer = set(['01', '10'])

        self.assertEqual(result, answer)

    def test_and_gate(self):
        a, b, c = self.controller.get_bit(3)

        self.controller.and_gate(a, b, c)

        result = self.get_result(a, b, c)
        answer = set(['000', '010', '100', '111'])

        self.assertEqual(result, answer)

    def test_or_gate(self):
        a, b, c = self.controller.get_bit(3)

        self.controller.or_gate(a, b, c)

        result = self.get_result(a, b, c)
        answer = set(['000', '011', '101', '111'])

        self.assertEqual(result, answer)

    def test_xor_gate(self):
        a, b, c = self.controller.get_bit(3)

        self.controller.xor_gate(a, b, c)

        result = self.get_result(a, b, c)
        answer = set(['000', '011', '101', '110'])

        self.assertEqual(result, answer)

    def test_xnor_gate(self):
        a, b, c = self.controller.get_bit(3)

        self.controller.xnor_gate(a, b, c)

        result = self.get_result(a, b, c)
        answer = set(['001', '010', '100', '111'])

        self.assertEqual(result, answer)

    def test_ctrl_select(self):
        a, b, ctrl, c = self.controller.get_bit(4)

        self.controller.ctrl_select(a, b, ctrl, c)

        result = self.get_result(a, b, ctrl, c)
        answer = set(['0000', '0100', '1001', '1101',
                     '0010', '0111', '1010', '1111'])

        self.assertEqual(result, answer)

    @parameterized.expand([(2, 6, 1, 6)])
    def test_ctrl_select_variable(self, A, B, control, C):
        a, b, c = self.controller.get_bits(3, 3, 3)
        ctrl = self.controller.get_bit()

        self.controller.ctrl_select_variable(a, b, ctrl, c)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)
        self.controller.set_bit_constant(ctrl, control)

        self.check_solution((c, C))

    @parameterized.expand([(1, 6, 6), (0, 6, 0)])
    def test_ctrl_var(self, control, A, C):
        a, c = self.controller.get_bits(3, 3)
        ctrl = self.controller.get_bit()

        self.controller.ctrl_var(ctrl, a, c)

        self.controller.set_variable_constant(a, A)
        self.controller.set_bit_constant(ctrl, control)

        self.check_solution((c, C))

    # def test_zero_gate(self):
    #     a = self.controller.get_bit()
    #     self.controller.zero_gate(a)
    #     lowest = self.controller.run_ExactSolver(True)
    #     a_ = self.controller.extract_bit(lowest.first, a)
    #     self.assertEqual(a_, 0)

    # def test_get_zero_bit(self):
    #     a = self.controller.get_zero_bit()
    #     self.check_change(a)
    #     self.check_solution((a, 0))

    # def test_one_gate(self):
    #     a = self.controller.get_bit()
    #     self.controller.one_gate(a)
    #     self.check_solution((a, 1))

    # def test_get_one_bit(self):
    #     a = self.controller.get_one_bit()
    #     self.check_solution((a, 1))


if __name__ == "__main__":
    unittest.main()
