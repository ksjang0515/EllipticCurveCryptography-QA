from ecc.controller.modulo_controller import ModuloController
from ecc.types import Bit, Binary, Name, Variable, Constant
from ecc.utilities import number_to_binary
from ecc.point import Point, PointConst

from tqdm import tqdm


class EccController(ModuloController):
    def __init__(self, P):
        super().__init__(P)

    def new_point(self) -> Point:
        x, y = self.get_bits(self.length, self.length)
        point = Point(x, y)
        return point

    def get_len_bit(self) -> Variable:
        return self.get_bit(self.length)

    def ctrl_select_point(self, A: Point, B: Point, ctrl: Bit, C: Point) -> None:
        self.ctrl_select_variable(A.x, B.x, ctrl, C.x)
        self.ctrl_select_variable(A.y, B.y, ctrl, C.y)

    def set_point_constant(self, point: Point, const_point: PointConst) -> None:
        self.set_variable_constant(point.x, const_point.x)
        self.set_variable_constant(point.y, const_point.y)

    def merge_point(self, point1: Point, point2: Point) -> None:
        self.merge_variable(point1.x, point2.x)
        self.merge_variable(point1.y, point2.y)

    def ecc_add(self, A: Point, B: PointConst, C: Point, ensure_modulo=False) -> None:
        """C = A + B"""

        if not (A.length == B.length == C.length == self.length):
            raise ValueError("Length does not match")

        # get lambda
        y_sub = self.get_len_bit()
        self.sub_const_modp(A.y, B.y, y_sub)  # y_A-y_B

        x_sub = self.get_len_bit()
        self.sub_const_modp(A.x, B.x, x_sub)  # x_A-x_B

        lambda_ = self.get_len_bit()
        self.div_modp(y_sub, x_sub, lambda_)  # lambda = (y_A-y_B) /(x_A-x_B)

        # get x_C
        lambda_squ = self.get_len_bit()
        self.square_modp(lambda_, lambda_squ)  # lambda^2

        x_C_temp = self.get_len_bit()
        self.sub_const_modp(lambda_squ, B.x, x_C_temp)  # lambda^2 -x_B
        self.sub_modp(x_C_temp, A.x, C.x,
                      ensure_modulo)  # x_C = lambda^2 -x_B -x_A

        # get y3
        # used sub_modp over sub_const_modp to not use point negation
        ancilla_x_B = self.get_len_bit()
        self.set_variable_constant(ancilla_x_B, B.x)
        x_B_sub = self.get_len_bit()
        self.sub_modp(ancilla_x_B, C.x, x_B_sub)  # x_B-x_C

        lambda_mult = self.get_len_bit()
        self.mult_modp(x_B_sub, lambda_, lambda_mult)  # lambda *(x_B-x_C)

        # y_C = lambda *(x_B-x_C) -y_B
        self.sub_modp(lambda_mult, B.y, C.y, ensure_modulo)

    def ecc_sub(self, A: Point, B: PointConst, C: Point, ensure_modulo=False) -> None:
        """C = A - B => A = B + C"""

        self.ecc_add(C, B, A)

        if ensure_modulo:
            self.ensure_modulo(C.x)
            self.ensure_modulo(C.y)

    def ecc_multiply(self, G_DOUBLES: list[PointConst], key: Variable, out_point: Point) -> None:
        """OUT = KEY * BASE"""

        if not (len(G_DOUBLES) == out_point.length == len(key) == self.length):
            raise ValueError("Length does not match")

        G = G_DOUBLES[0]

        base_point = self.get_bits(self.length, self.length)
        # start from G because implementing point at infinity is expensive
        pre_point = base_point

        for i in tqdm(range(self.length)):
            # ecc add
            ancilla_add = self.new_point()
            self.ecc_add(pre_point, G_DOUBLES[i], ancilla_add)

            # add if bit is 1
            new_point = self.new_point()
            self.ctrl_select_point(pre_point, ancilla_add, key[i], new_point)

            pre_point = new_point

        # subtract G because we started from G
        new_point = self.new_point()
        self.ecc_sub(pre_point, base_point, new_point)

        self.merge_point(new_point, out_point)
        self.set_point_constant(base_point, G)
