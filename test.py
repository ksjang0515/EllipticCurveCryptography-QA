from ecc import EccController

ecc = EccController(5)
a = ecc.create_variable("a", 3)
c = ecc.create_variable("c", 3)

ecc.mult_inv_modp(a, c, ensure_modulo=True)
print("DONE")
# 51

ecc.set_variable_constant(a, 3)
# 48
print("DONE")
