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
        c_length = max(a_length, b_length)+1

        a, b, c = self.controller.get_bits(a_length, b_length, c_length)

        self.controller.add(a, b, c)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        self.check_solution((c, C))

    @parameterized.expand([(3, 6, 3), (7, 3, 3)])
    def test_add_const(self, A: int, B: int, a_length: int):
        C = A+B

        a, c = self.controller.get_bits(a_length, a_length+1)
        b = ecc.number_to_binary(B)

        self.controller.add_const(a, b, c)

        self.controller.set_variable_constant(a, A)

        self.check_solution((c, C))

    @parameterized.expand([(3, 4), (3, 3), (6, 4)])
    def test_subtract(self, A: int, B: int):
        C = (A-B) % (2**3)
        underflow = 1 if A < B else 0

        a, b, c = self.controller.get_bits(3, 3, 3)
        u = self.controller.get_bit()

        self.controller.subtract(a, b, c, u)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        self.check_solution((c, C), (u, underflow))

    @parameterized.expand([(3, 4, 3), (3, 3, 3), (6, 4, 3)])
    def test_subtract_const(self, A: int, B: int, a_length: int):
        C = (A-B) % (2**3)
        underflow = 1 if A < B else 0

        a, c = self.controller.get_bits(a_length, a_length)
        u = self.controller.get_bit()
        b = ecc.number_to_binary(B)

        self.controller.subtract_const(a, b, c, u)

        self.controller.set_variable_constant(a, A)

        self.check_solution((c, C), (u, underflow))

    @parameterized.expand([(5, 7), (6, 3), (1, 3), (2, 7), (5, 1)])
    def test_multiply(self, A, B):
        C = A*B

        a, b, c = self.controller.get_bits(3, 3, 6)

        self.controller.multiply(a, b, c)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        self.check_solution((c, C))

    # checked (5, 1) by hand because it will return empty sample
    @parameterized.expand([(5, 7), (6, 3), (1, 3), (2, 7)])
    def test_multiply_const(self, A, B):
        C = A*B
        a = self.controller.get_bit(3)
        b = ecc.number_to_binary(B)
        c_length = len(a) if len(b) == 1 else len(a) + len(b)
        c = self.controller.get_bit(c_length)

        self.controller.multiply_const(a, b, c)

        self.controller.set_variable_constant(a, A)

        self.check_solution((c, C))

    @parameterized.expand([(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,)])
    def test_square(self, A):
        C = A**2

        a, c = self.controller.get_bits(3, 6)

        self.controller.square(a, c)

        self.controller.set_variable_constant(a, A)

        self.check_solution((c, C))


if __name__ == "__main__":
    unittest.main()
