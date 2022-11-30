from ecc import EccController

ecc = EccController(13)

G = (3, 5)
x = ecc.create_variable('x', 4)
y = ecc.create_variable('y', 4)
key = ecc.create_variable('key', 4)

ecc.ecc_multiply(G[0], G[1], x, y, key)

number_of_qubits = len(ecc.bqm.linear)
print(f'{number_of_qubits}')
