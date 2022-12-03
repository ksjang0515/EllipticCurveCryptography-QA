import ecc
import unittest
from parameterized import parameterized
from typing import Union

from tests import base


class TestArithmeticController(base.Base):
    def setUp(self) -> None:
        self.controller = ecc.ArithmeticController()

    @parameterized.expand([(3, 6, 3, 3), (7, 3, 3, 2), (3, 6, 2, 3)])
    def test_add(self, A: int, B: int, a_length: int, b_length: int):
        C = A+B

        a = self.controller.get_bits(a_length)
        b = self.controller.get_bits(b_length)
        c = self.controller.get_bits(max(a_length, b_length)+1)

        self.controller.add(a, b, c)

        self.check_change(a, b, c)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        self.check_solution((c, C))

    @parameterized.expand([(3, 6, 3), (7, 3, 3)])
    def test_add_const(self, A: int, B: int, a_length: int):
        C = A+B

        a = self.controller.get_bits(a_length)
        b = ecc.number_to_binary(B)
        c = self.controller.get_bits(a_length+1)

        self.controller.add_const(a, b, c)

        self.check_change(a)

        self.controller.set_variable_constant(a, A)

        self.check_solution((c, C))

    @parameterized.expand([(3, 4), (3, 3), (6, 4)])
    def test_subtract(self, A: int, B: int):
        C = A-B if A >= B else 2**3 + A - B
        underflow = 1 if A < B else 0

        a = self.controller.get_bits(3)
        b = self.controller.get_bits(3)
        c = self.controller.get_bits(3)
        u = self.controller.get_bit()

        self.controller.subtract(a, b, c, u)

        self.check_change(a, b, c, u)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        self.check_solution((c, C), (u, underflow))

    @parameterized.expand([(5, 7), (6, 3), (1, 3), (2, 7)])
    def test_multiply(self, A, B):
        C = A*B

        a = self.controller.get_bits(3)
        b = self.controller.get_bits(3)
        c = self.controller.get_bits(6)

        self.controller.multiply(a, b, c)

        self.check_change(a, b, c)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        self.check_solution((c, C))


if __name__ == "__main__":
    unittest.main()
