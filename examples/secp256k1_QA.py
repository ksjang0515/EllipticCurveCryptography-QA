from ecc.point import PointConst
from ecc import EccController
from ecc.data.secp256k1.base import secp256k1_params

import json

# init controller
p = secp256k1_params['P']
controller = EccController(p)

# load doubles
with open('ecc/data/secp256k1/doubles.json', 'r') as f:
    j = json.load(f)

doubles = []
for i in range(256):
    d = j[f'{i}']
    point = PointConst(d['x'], d['y'])
    doubles.append(point)

# run ecc_mult
key = controller.get_bit(256)
out_point = controller.new_point()
controller.ecc_multiply(doubles, key, out_point)


print(controller.shape)
print("DONE")
