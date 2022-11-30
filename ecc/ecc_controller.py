from ecc.base_controller import Controller, VariableType, ConstantType
from ecc.utilities import number_to_binary


class EccController(Controller):
    def __init__(self, P, a=7):
        self.P = P
        self.P_CONST = number_to_binary(P)
        self.length = len(self.P_CONST)

        self.a = a

        super().__init__()

    def ensure_modulo(self, A: VariableType) -> None:
        """ensure that A is less than P"""
        a = self.check_VariableType(A)

        if len(a) != self.length:
            raise ValueError("Length does not match")

        ancilla_sub = self.get_bits(self.length)
        p = self.get_bits(self.length)
        underflow = self.get_bit()

        self.subtract(p, a, ancilla_sub, underflow)
        self.zero_gate(underflow)

        self.set_variable_constant(p, self.P_CONST)

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

    def ecc_add(
        self,
        X1: VariableType,
        Y1: VariableType,
        X2: VariableType,
        Y2: VariableType,
        X3: VariableType,
        Y3: VariableType,
        ensure_modulo=False,
    ) -> None:
        """(X1, Y1) + (X2, Y2) = (X3, Y3)"""

        x1 = self.check_VariableType(X1)
        y1 = self.check_VariableType(Y1)
        x2 = self.check_VariableType(X2)
        y2 = self.check_VariableType(Y2)
        x3 = self.check_VariableType(X3)
        y3 = self.check_VariableType(Y3)

        if (
            len(x1)
            == len(y1)
            == len(x2)
            == len(y2)
            == len(x3)
            == len(y3)
            == self.length
        ):
            pass
        else:
            raise ValueError("Length does not match")

        # get lambda
        y_sub = self.get_bits(self.length)
        self.sub_modp(y2, y1, y_sub)  # y2-y1

        x_sub = self.get_bits(self.length)
        self.sub_modp(x2, x1, x_sub)  # x2-x1

        lambda_ = self.get_bits(self.length)
        self.div_modp(y_sub, x_sub, lambda_)  # lambda = (y2-y1) /(x2-x1)

        # get x3
        lambda_squ = self.get_bits(self.length)
        self.square_modp(lambda_, lambda_squ)  # lambda^2

        x3_temp = self.get_bits(self.length)
        self.sub_modp(lambda_squ, x1, x3_temp)  # lambda^2 -x1
        self.sub_modp(x3_temp, x2, x3, ensure_modulo)  # x3 = lambda^2 -x1 -x2

        # get y3
        x1_sub = self.get_bits(self.length)
        self.sub_modp(x1, x3, x1_sub)  # x1-x3

        lambda_mult = self.get_bits(self.length)
        self.mult_modp(x1_sub, lambda_, lambda_mult)  # lambda *(x1-x3)
        # y3 = lambda(x1-x3) -y1
        self.sub_modp(lambda_mult, y1, y3, ensure_modulo)

    def ecc_multiply(
        self,
        G: tuple[int, int],
        G_DOUBLES: list[tuple[int, int]],
        KEY: VariableType,
        X_OUT: VariableType,
        Y_OUT: VariableType,
    ):
        """(X_OUT, Y_OUT) = KEY * (X_BASE, Y_BASE)"""
        x_out = self.check_VariableType(X_OUT)
        y_out = self.check_VariableType(Y_OUT)
        key = self.check_VariableType(KEY)

        if len(G_DOUBLES) == len(x_out) == len(y_out) == len(key) == self.length:
            pass
        else:
            raise ValueError("Length does not match")

        x_base = self.get_bits(self.length)
        y_base = self.get_bits(self.length)

        pre_x = x_base
        pre_y = y_base

        for i in range(self.length):
            # ecc add
            ancilla_G_x = self.get_bits(self.length)
            ancilla_G_y = self.get_bits(self.length)

            ancilla_add_x = self.get_bits(self.length)
            ancilla_add_y = self.get_bits(self.length)
            self.ecc_add(pre_x, pre_y, ancilla_G_x, ancilla_G_y,
                         ancilla_add_x, ancilla_add_y)

            self.set_variable_constant(ancilla_G_x, G_DOUBLES[i][0])
            self.set_variable_constant(ancilla_G_y, G_DOUBLES[i][1])

            # add if ctrl
            new_x = self.get_bits(self.length)
            new_y = self.get_bits(self.length)
            self.ctrl_select_variable(pre_x, ancilla_add_x, key[i], new_x)
            self.ctrl_select_variable(pre_y, ancilla_add_y, key[i], new_y)

            pre_x = new_x
            pre_y = new_y

        # subtract G
        """(X1, Y1) - (X2, Y2) = (X3, Y3) => (X2, Y2) + (X3, Y3) = (X1, Y1)"""
        new_x = self.get_bits(self.length)
        new_y = self.get_bits(self.length)
        self.ecc_add(new_x, new_y, x_base, y_base, pre_x, pre_y)

        for i in range(self.length):
            x_out[i].index = new_x[i].index
            y_out[i].index = new_y[i].index

        self.set_variable_constant(x_base, G[0])
        self.set_variable_constant(y_base, G[1])
