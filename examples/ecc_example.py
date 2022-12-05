from ecc import EccController

ecc = EccController(2**256-1)

G = (3, 5)
x = ecc.create_variable('x', 256)
y = ecc.create_variable('y', 256)
key = ecc.create_variable('key', 256)

ecc.ecc_multiply(G[0], G[1], key, x, y)

number_of_qubits = len(ecc.bqm.linear)
print(f'{number_of_qubits}')
