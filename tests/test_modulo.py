import ecc
import unittest
from parameterized import parameterized
from typing import Union

from tests import base

"""
Can't create test for multiply and it's derivatives because it's too big to calculate on classical computer
"""


class TestModuloController(base.Base):
    def setUp(self) -> None:
        self.P = 5
        self.controller = ecc.ModuloController(self.P)

        self.data_dir = "tests/data/modulo"

    def test_ensure_modulo(self):
        a = self.controller.get_bit(3)

        self.controller.ensure_modulo(a)

        result = self.get_result(a)
        answer = self.get_answer('test_ensure_modulo.txt')

        self.assertEqual(result, answer)

    def test_modulo_p_ensure_modulo(self):
        a, r = self.controller.get_bits(5, 3)

        self.controller.modulo_p(a, r, True)

        result = self.get_result(a, r)

        answer = self.get_answer('test_modulo_p_ensure_modulo.txt')

        self.assertEqual(result, answer)

    def test_modulo_p(self):
        a, r = self.controller.get_bits(5, 3)

        self.controller.modulo_p(a, r)

        result = self.get_result(a, r)
        answer = self.get_answer('test_modulo_p.txt')

        self.assertEqual(result, answer)

    @parameterized.expand([(1, 3), (3, 4), (0, 0), (2, 3)])
    def test_add_modp_ensure_modulo(self, A, B):
        C = (A+B) % self.P
        a, b, c = self.controller.get_bits(3, 3, 3)

        self.controller.add_modp(a, b, c, True)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        self.check_solution((c, C))

    # for case (0, 0, '000') cannot result in '101', however it doesn't matter as ensure_modulo is False
    # needs a better assert method
    @parameterized.expand([(1, 3, '001'), (3, 4, '010', '111'), (0, 0, '000'), (2, 3, '000', '101')])
    def test_add_modp(self, A, B, *args):
        a, b, c = self.controller.get_bits(3, 3, 3)

        self.controller.add_modp(a, b, c)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        result = self.get_result(c)
        answer = set(args)

        self.assertEqual(result, answer)

    @parameterized.expand([(1, 3), (3, 4), (0, 0), (2, 3)])
    def test_add_const_modp_ensure_modulo(self, A, B):
        C = (A+B) % self.P
        a, c = self.controller.get_bits(3, 3)
        b = ecc.number_to_binary(B, 3)

        self.controller.add_const_modp(a, b, c, True)

        self.controller.set_variable_constant(a, A)

        self.check_solution((c, C))

    @parameterized.expand([(1, 3, '001'), (3, 4, '010', '111'), (0, 0, '000'), (2, 3, '000', '101')])
    def test_add_const_modp(self, A, B, *args):
        a, c = self.controller.get_bits(3, 3)
        b = ecc.number_to_binary(B)

        self.controller.add_const_modp(a, b, c)

        self.controller.set_variable_constant(a, A)

        result = self.get_result(c)
        answer = set(args)

        self.assertEqual(result, answer)

    @parameterized.expand([(1, 3), (4, 3), (2, 0), (3, 3)])
    def test_sub_modp_ensure_modulo(self, A, B):
        C = (A-B) % self.P
        a, b, c = self.controller.get_bits(3, 3, 3)

        self.controller.sub_modp(a, b, c, True)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        self.check_solution((c, C))

    @parameterized.expand([(1, 3, '110'), (4, 3, '100', '011'), (2, 0, '010', '111'), (3, 3, '000', '101')])
    def test_sub_modp(self, A, B, *args):
        a, b, c = self.controller.get_bits(3, 3, 3)

        self.controller.sub_modp(a, b, c)

        self.controller.set_variable_constant(a, A)
        self.controller.set_variable_constant(b, B)

        result = self.get_result(c)
        answer = set(args)

        self.assertEqual(result, answer)

    @parameterized.expand([(1, 3), (4, 3), (2, 0), (3, 3)])
    def test_sub_const_modp_ensure_modulo(self, A, B):
        C = (A-B) % self.P
        a, c = self.controller.get_bits(3, 3)
        b = ecc.number_to_binary(B, 3)

        self.controller.sub_const_modp(a, b, c, True)

        self.controller.set_variable_constant(a, A)

        self.check_solution((c, C))

    @parameterized.expand([(1, 3, '110'), (4, 3, '100', '011'), (2, 0, '010', '111'), (3, 3, '000', '101')])
    def test_sub_const_modp(self, A, B, *args):
        a, c = self.controller.get_bits(3, 3)
        b = ecc.number_to_binary(B, 3)

        self.controller.sub_const_modp(a, b, c)

        self.controller.set_variable_constant(a, A)

        result = self.get_result(c)
        answer = set(args)

        self.assertEqual(result, answer)


if __name__ == "__main__":
    unittest.main()
