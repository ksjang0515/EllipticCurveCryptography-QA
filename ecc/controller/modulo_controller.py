from ecc.controller.arithmetic_controller import ArithmeticController
from ecc.types import VariableType, ConstantType, Bit
from ecc.utilities import number_to_binary


class ModuloController(ArithmeticController):
    def __init__(self, P):
        self.P = P
        self.P_CONST = number_to_binary(P)
        self.length = len(self.P_CONST)

        super().__init__()

    def ensure_modulo(self, A: VariableType) -> None:
        """ensure that A is less than P"""
        a = self.check_VariableType(A)

        if len(a) != self.length:
            raise ValueError("Length does not match")

        ancilla_sub = self.get_bits(self.length)
        underflow = self.get_one_bit()

        self.subtract_const_simple(a, self.P_CONST, ancilla_sub, underflow)

    def modulo_p(self, A: VariableType, R: VariableType, ensure_modulo=False):
        """R = A mod p
        calculates A = m*P + R"""

        a = self.check_VariableType(A)
        r = self.check_VariableType(R)

        if len(r) != self.length:
            raise ValueError("Length does not match")

        a_length = len(a)
        if a_length < self.length:
            raise ValueError("A is too short")

        m_length = a_length - self.length if a_length != self.length else 1
        m = self.get_bits(m_length)
        ancilla_mult = self.get_bits(a_length)

        self.multiply_const(m, self.P_CONST, ancilla_mult)
        self.add_no_overflow(ancilla_mult, r, a)

        if ensure_modulo:
            self.ensure_modulo(r)

    def add_modp(
        self, A: VariableType, B: VariableType, C: VariableType, ensure_modulo=False
    ) -> None:
        """C = (A+B) mod p"""

        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        if len(a) == len(b) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        ancilla = self.get_bits(self.length + 1)
        self.add(a, b, ancilla)

        self.modulo_p(ancilla, c, ensure_modulo)

    def add_const_modp(
        self, A: VariableType, B: ConstantType, C: VariableType, ensure_modulo=False
    ) -> None:
        """C = (A+B) mod p"""

        a = self.check_VariableType(A)
        b = self.check_ConstantType(B)
        c = self.check_VariableType(C)

        if len(a) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        if len(b) > self.length:
            raise ValueError(
                "length of B is too long and performance is not checked")

        ancilla_add = self.get_bits(self.length + 1)
        ancilla_b = self.get_bits(len(b))
        self.add(a, ancilla_b, ancilla_add)
        self.set_variable_constant(ancilla_b, b)

        self.modulo_p(ancilla_add, c, ensure_modulo)

    def sub_modp(
        self, A: VariableType, B: VariableType, C: VariableType, ensure_modulo=False
    ) -> None:
        """C = (A-B) mod p"""

        self.add_modp(B, C, A, ensure_modulo)

    def mult_modp(
        self, A: VariableType, B: VariableType, C: VariableType, ensure_modulo=False
    ) -> None:
        """C = (A*B) mod p"""

        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        if len(a) == len(b) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        ancilla_mult = self.get_bits(2 * self.length)
        self.multiply(a, b, ancilla_mult)

        self.modulo_p(ancilla_mult, c, ensure_modulo)

    def mult_const_modp(
        self,
        A: VariableType,
        B: ConstantType,
        C: VariableType,
        ensure_modulo=False,
    ) -> None:
        """C = (A*B) mod p"""
        a = self.check_VariableType(A)
        b = self.check_ConstantType(B)
        c = self.check_VariableType(C)

        if len(a) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        ancilla_mult_length = len(a) + len(b) if len(b) != 1 else len(a)
        ancilla_mult = self.get_bits(ancilla_mult_length)
        self.multiply_const(a, b, ancilla_mult)

        self.modulo_p(ancilla_mult, c, ensure_modulo)

    def square_modp(
        self, A: VariableType, C: VariableType, ensure_modulo=False
    ) -> None:
        """C = (A^2) mod p"""

        a = self.check_VariableType(A)
        c = self.check_VariableType(C)

        if len(a) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        ancilla_squ = self.get_bits(2 * self.length)
        self.square(a, ancilla_squ)

        self.modulo_p(ancilla_squ, c, ensure_modulo)

    def mult_inv_modp(
        self, A: VariableType, C: VariableType, ensure_modulo=False
    ) -> None:
        """(A*C) mod p = 1 mod p"""
        a = self.check_VariableType(A)
        c = self.check_VariableType(C)

        if len(a) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        r = self.get_bits(self.length)
        self.mult_modp(a, c, r)

        self.set_variable_constant(r, 1)

        if ensure_modulo:
            self.ensure_modulo(c)

    def inv_modp(self, A: VariableType, C: VariableType, ensure_modulo=False) -> None:
        """alias of mult_int_modp"""
        self.mult_inv_modp(A, C, ensure_modulo)

    def div_modp(
        self, A: VariableType, B: VariableType, C: VariableType, ensure_modulo=False
    ) -> None:
        """C = (A/B) mod p => A = (B*C) mod p"""

        self.mult_modp(B, C, A, ensure_modulo)

    def double_modp(
        self, A: VariableType, C: VariableType, ensure_modulo=False
    ) -> None:
        """C = (2*A) mod p"""
        a = self.check_VariableType(A)
        c = self.check_VariableType(C)

        if len(a) == len(c) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        b = self.get_bit()
        double = [b, *a]  # 2*A

        self.modulo_p(double, c, ensure_modulo)
