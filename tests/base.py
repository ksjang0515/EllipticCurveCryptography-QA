import ecc
import unittest
from typing import Union


class Base(unittest.TestCase):
    def check_solution(self, *check_list: Union[tuple[ecc.Bit, int], tuple[list[ecc.Bit], Union[list[int], int]]]):
        solution = self.controller.run_ExactSolver()
        lowest = solution.lowest()

        self.assertEqual(len(lowest), 1, "More than one lowest state")
        self.assertEqual(lowest.record[0].energy, 0, "Energy is not zero")

        sample = lowest.samples()[0]

        for out, expected in check_list:
            if isinstance(out, ecc.Bit):
                result = self.controller.extract_bit(sample, out)
            else:
                if isinstance(expected, int):
                    expected = ecc.number_to_binary(expected, len(out))

                result = self.controller.extract_variable(sample, out)

            self.assertEqual(result, expected, "Wrong result")

    def check_change(self, *args):
        for bit in args:
            if isinstance(bit, list):
                for b in bit:
                    self.assertFalse(b.changed, "Bit changed")

                continue

            self.assertFalse(bit.changed, "Bit changed")
