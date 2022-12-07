from ecc.point import PointConst


def ecc_double(A: PointConst, a: int, p) -> PointConst:
    lambda_ = ((3*(A.x_int**2) + a) * pow(2*A.y_int, -1, p)) % p

    x = ((lambda_ ** 2) - (2*A.x_int)) % p
    y = (lambda_ * (A.x_int - x) - A.y_int) % p

    C = PointConst(x, y)
    return C
