import ecc
import unittest
from parameterized import parameterized
from typing import Union

from tests import base


class TestModuloController(base.Base):
    def setUp(self) -> None:
        self.P = 5
        self.controller = ecc.ModuloController(self.P)

    def test_ensure_modulo(self):
        a = self.controller.get_bits(3)

        self.controller.ensure_modulo(a)

        solution = self.controller.run_ExactSolver()
        lowest = solution.lowest()

        a_ = set()
        for s in lowest:
            x = self.controller.extract_variable(s, a)
            a_.add(f'{x[0]}{x[1]}{x[2]}')

        answer = set(('000', '100', '010', '110', '001'))

        self.assertEqual(a_, answer)

    # @parameterized.expand([(0, ), (1, ), (2, ), (3, ), (4, ), (5, ), (6, ), (7, )])
    # def test_modulo_p(self, A: int):
    #     R = A % self.P
    #     a = self.controller.get_bits(3)
    #     r = self.controller.get_bits(3)

    #     self.controller.modulo_p(a, r, True)

    #     self.check_change(a, r)

    #     self.controller.set_variable_constant(a, A)

    #     self.check_solution((r, R))


if __name__ == "__main__":
    unittest.main()
