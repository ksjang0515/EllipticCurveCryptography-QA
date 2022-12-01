from ecc.controller.modulo_controller import ModuloController
from ecc.types import VariableType, ConstantType, Bit
from ecc.utilities import number_to_binary


class EccController(ModuloController):
    def __init__(self, P, a=7):
        super().__init__(P)

        self.a = a

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

    def ecc_sub(
        self,
        X1: VariableType,
        Y1: VariableType,
        X2: VariableType,
        Y2: VariableType,
        X3: VariableType,
        Y3: VariableType,
        ensure_modulo=False,
    ) -> None:
        """(X3, Y3) = (X1, Y1) - (X2, Y2) => (X1, Y1) = (X2, Y2) + (X3, Y3)"""

        self.ecc_add(X2, Y2, X3, Y3, X1, Y1)

        if ensure_modulo:
            self.ensure_modulo(X3)
            self.ensure_modulo(Y3)

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
        new_x = self.get_bits(self.length)
        new_y = self.get_bits(self.length)
        self.ecc_sub(pre_x, pre_y, x_base, y_base, new_x, new_y)

        for i in range(self.length):
            x_out[i].index = new_x[i].index
            y_out[i].index = new_y[i].index

        self.set_variable_constant(x_base, G[0])
        self.set_variable_constant(y_base, G[1])
