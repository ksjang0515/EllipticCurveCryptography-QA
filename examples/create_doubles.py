from ecc.utilities.ecc_double import ecc_double
from ecc.data.secp256k1.base import BASE, secp256k1_params

import json

a = secp256k1_params['A']
p = secp256k1_params['P']
point = BASE
data = {}

data[0] = {
    'x': point.x_int,
    'y': point.y_int
}

for i in range(1, 256):
    new_point = ecc_double(point, a, p)
    data[i] = {
        'x': new_point.x_int,
        'y': new_point.y_int
    }
    point = new_point

with open('ecc/data/secp256k1/doubles.json', 'w') as f:
    json.dump(data, f)
