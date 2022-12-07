from ecc.controller.arithmetic_controller import ArithmeticController
from ecc.types import Variable, Constant
from ecc.utilities import number_to_binary


class ModuloController(ArithmeticController):
    def __init__(self, P):
        self.P = P
        self.P_CONST = number_to_binary(P)
        self.length = len(self.P_CONST)

        super().__init__()

    def ensure_modulo(self, a: Variable) -> None:
        """ensure that A is less than P"""

        if len(a) != self.length:
            raise ValueError("Length does not match")

        ancilla_sub = self.get_bit(self.length)
        underflow = self.get_one_bit()

        self.subtract_const(a, self.P_CONST, ancilla_sub, underflow)

    def modulo_p(self, a: Variable, r: Variable, ensure_modulo=False):
        """r = a mod p
        calculates A = m*P + R"""

        if len(r) != self.length:
            raise ValueError("Length does not match")

        a_length = len(a)
        if a_length < self.length:
            raise ValueError("A is too short")

        m_length = a_length - self.length + 1
        m, ancilla_mult = self.get_bits(m_length, a_length)
        zero = self.get_zero_bit()
        ancilla_mult_ = [*ancilla_mult, zero]

        self.multiply_const(m, self.P_CONST, ancilla_mult_)
        self.add_no_overflow(ancilla_mult, r, a)

        if ensure_modulo:
            self.ensure_modulo(r)

    def add_modp(
        self, a: Variable, b: Variable, c: Variable, ensure_modulo=False
    ) -> None:
        """c = (a+b) mod p"""

        if not (len(a) == len(b) == len(c) == self.length):
            raise ValueError("Length does not match")

        ancilla = self.get_bit(self.length + 1)
        self.add(a, b, ancilla)

        self.modulo_p(ancilla, c, ensure_modulo)

    def add_const_modp(self, a: Variable, b: Constant, c: Variable, ensure_modulo=False) -> None:
        """c = (a+b) mod p"""

        b = self.check_ConstantType(b)

        if not (len(a) == len(c) == self.length):
            raise ValueError("Length does not match")

        if len(b) > self.length:
            raise ValueError(
                "length of B is too long and performance is not checked")

        ancilla_add = self.get_bit(self.length + 1)
        self.add_const(a, b, ancilla_add)

        self.modulo_p(ancilla_add, c, ensure_modulo)

    def sub_modp(self, a: Variable, b: Variable, c: Variable, ensure_modulo=False) -> None:
        """c = (a-b) mod p"""

        self.add_modp(b, c, a, ensure_modulo)

    def sub_const_modp(self, a: Variable, b: Constant, c: Variable, ensure_modulo=False) -> None:
        """c = (a-b) mod p"""

        self.add_const_modp(c, b, a, ensure_modulo)

    def mult_modp(self, a: Variable, b: Variable, c: Variable, ensure_modulo=False) -> None:
        """c = (a*b) mod p"""

        if len(a) == len(b) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        ancilla_mult = self.get_bit(2 * self.length)
        self.multiply(a, b, ancilla_mult)

        self.modulo_p(ancilla_mult, c, ensure_modulo)

    def mult_const_modp(self, a: Variable, b: Constant, c: Variable, ensure_modulo=False) -> None:
        """c = (a*b) mod p"""
        b = self.check_ConstantType(b)

        if len(a) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        ancilla_mult_length = len(a) + len(b) if len(b) != 1 else len(a)
        ancilla_mult = self.get_bit(ancilla_mult_length)
        self.multiply_const(a, b, ancilla_mult)

        self.modulo_p(ancilla_mult, c, ensure_modulo)

    def square_modp(self, a: Variable, c: Variable, ensure_modulo=False) -> None:
        """c = (a^2) mod p"""

        if len(a) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        ancilla_squ = self.get_bit(2 * self.length)
        self.square(a, ancilla_squ)

        self.modulo_p(ancilla_squ, c, ensure_modulo)

    def mult_inv_modp(
        self, a: Variable, c: Variable, ensure_modulo=False
    ) -> None:
        """(a*c) mod p = 1 mod p"""

        if len(a) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        r = self.get_bit(self.length)
        self.mult_modp(a, c, r)

        self.set_variable_constant(r, 1)

        if ensure_modulo:
            self.ensure_modulo(c)

    def inv_modp(self, a: Variable, c: Variable, ensure_modulo=False) -> None:
        """alias of mult_int_modp"""
        self.mult_inv_modp(a, c, ensure_modulo)

    def div_modp(self, a: Variable, b: Variable, c: Variable, ensure_modulo=False) -> None:
        """c = (a/b) mod p => a = (b*c) mod p"""

        self.mult_modp(b, c, a, ensure_modulo)

    def double_modp(
        self, a: Variable, c: Variable, ensure_modulo=False
    ) -> None:
        """c = (2*a) mod p"""

        if len(a) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        b = self.get_bit()
        double = [b, *a]  # 2*A

        self.modulo_p(double, c, ensure_modulo)
