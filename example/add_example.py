from ecc import EccController

ecc = EccController(13)

x = ecc.create_variable('x', 3)
y = ecc.create_variable('y', 3)
z = ecc.create_variable('z', 4)

ecc.add(x, y, z)

ecc.set_variable_constant('x', 5)
ecc.set_variable_constant(y, 7)

solution = ecc.run_ExactSolver()
Z = ecc.extract_variable(solution.first, z)

print(Z)
