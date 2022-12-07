from ecc.point import PointConst


def ecc_double(A: PointConst, a: int, p) -> PointConst:
    lambda_ = ((3*(A.x**2) + a) * pow(2*A.y, -1, p)) % p

    x = ((lambda_ ** 2) - (2*A.x)) % p
    y = (lambda_ * (A.x - x) - A.y) % p

    C = PointConst(x, y)
    return C
