import ecc
from ecc.types import Bit, Variable, Binary, Constant
import unittest
from typing import Union


class Base(unittest.TestCase):
    def check_solution(self, *check_list: Union[tuple[Bit, Binary], tuple[Variable, Constant]]):
        solution = self.controller.run_ExactSolver()
        lowest = solution.lowest()

        self.assertEqual(len(lowest), 1, "More than one lowest state")
        self.assertEqual(lowest.record[0].energy, 0, "Energy is not zero")

        sample = lowest.samples()[0]

        for out, expected in check_list:
            if isinstance(out, Bit):
                result = self.controller.extract_bit(sample, out)
            else:
                if isinstance(expected, int):
                    expected = ecc.number_to_binary(expected, len(out))

                result = self.controller.extract_variable(sample, out)

            self.assertEqual(result, expected, "Wrong result")

    def get_result(self, *args) -> set[str]:
        lowest = self.controller.run_ExactSolver(True)

        result = set()
        for s in lowest:
            extracted = self.controller.extract(s, *args)
            r = ''
            for e in extracted:
                if isinstance(e, Binary):
                    r += str(e)
                else:
                    for b in e:
                        r += str(b)

            result.add(r)

        return result
