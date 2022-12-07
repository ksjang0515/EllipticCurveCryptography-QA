# Elliptic Curve Cryptography Implementation using Dwave's Ocean SDK

There are many research on breaking cryptography using gate based quantum computer. However there are many challenges to overcome on which I believe can be easily done using a quantum annealer. For example, as shown [here](https://link.springer.com/chapter/10.1007/978-3-319-70697-9_9), modular multiplicative inverse is the most expensive arithmetic operation in implementing ECC on quantum computer. But for quantum annealer, it's simple as doing one multiplication and addition. Furthermore instead of calculating inverse, division can be used, making it even more simple. This is explained in detail with other advantages at Implementation Details section.

It does have some drawbacks, such as nonreusable ancilla bits, requiring more bits than gate-based quantum computer.

# Glossary

### Bit

Represents a single bit. Used at upper level.

---

### Variable

Represents a list of bits.

---

### Name

Represents bit's name(equivalent to dimod's variable). Used at lower level for interacting with BinaryQuadraticModel.

---

### Constant

(1) Mapping from bit to constant binary. Constant values are set before running solver to make it more flexible, allowing interaction between constant and bit.

(2) Fixed value, usually known before the computation. Used to indicate method's parameter.

---

### Controller

Controls creation and interaction of bits, separated by 6 different parts.

# Approach

Main concept came up while reading [this paper](https://arxiv.org/abs/2005.02268) (where it's main idea dates back to [2017](https://www.nature.com/articles/srep43048)). By building boolean logic gates on quantum annealer, it can be used to solve equations. Also this idea can be expanded to thinking some parts of the equation fixed and others free allowing it to be optimized to solution. More details will be provided in the Implementation Details section.

# Implementation Details

## Arithmetic Operations

Some obvious operations are not mentioned, such as Square. However Add and Multiply is shown becuase it is used as basis of other operations.

---

### Add

**A+B = C**

Consider A and B as fixed.

---

### Subtract

**A-B = C**

Consider A and B as fixed and modify equation to **B+C = A**.

---

### Multiply

**A\*B = C**

Consider A and B as fixed.

---

### Modulo

**A (mod p) = C**

Consider A as fixed, p constant and using unknown variable m, above equation can be changed to **m\*p + C = A**. This makes modulo operation cheap. Thus, removes the need for modulo operation at every step like shown [here](https://link.springer.com/chapter/10.1007/978-3-319-70697-9_9)(Modular Multiplication section).

However Modulo design have a minor flaw. For n bit variable C, if C+p is less than 2<sup>n</sup>, C could result in either C or C+p. Since additional p will be ignored in the next modulo operation, this isn't a major concern. But at the last step of ECC Multiply this is required. To ensure operation's result is less than p, Ensure Modulo can be used.

---

### Ensure Modulo

**A-p = s, set underflow bit to one**

Consider A fixed, constant p, unknown Variable s and unknown Bit underflow. Setting underflow to one will create a bias to result that is less than p.

---

### Divide mod p

**A/B (mod p) = C**

Consider A and B as fixed, which makes it same as **B\*C (mod p) = A**. Removing the need for modular multiplicative inverse.

---

### Modular Multiplicative Inverse

**A\*C (mod p) = 1**

Consider A as fixed, set result to constant 1. This makes modular multiplicative inverse, the most expensive operation, as easy as modular multiplication. However since divide can be implemented as described above, this is not used in ECC implementation.

---

### Control Select

**c = b if ctrl is 1, else a**

Consider fixed bit a, b, and ctrl, c is selected either a or b. Used for implementing ECC Multiply.

## ECC Operations

[ECC Double](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Point_doubling) can be implemented, but to reduce the number of bits, it is not used.

---

### [ECC Add](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Point_addition)

**A+B = C**

For fixed point A, constant point B, calculate point C.

---

### [ECC Mutiply](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Double-and-add) (Iterative algorithm, index increasing)

**key\*G = OUT**

For unknown variable key, constant base point G, calculate point C. Since point at infinity is expensive to implement in quantum annealer, it starts on point G resulting in **(key+1)\*G**. G is later subtracted to get **key\*G**. It uses precalculated doubles of G, removing the need for ECC Double and reduce the number of bits used. Control Select is used to add doubled G if current key's bit is 1.

## Controller

Controller is divided into 6 classes, separated by roles. Sequently inheriting the other.

---

### Base Controller

Controls setting interaction and running solvers.

---

### Bit Controller

Controls mapping from Bit to Name, setting constant values, extracting result, and merging bits.

---

### Gate Controller

Controls Bit operations, such as fulladder gate, boolean logic gates.

---

### Arithmetic Controller

Controls basic arithmetic operations, such as add, multiply.

---

### Modulo Controller

Controls modular arithmetic operations, such as add_modp, mult_modp

---

### ECC Controller

Controls ECC operations, such as ecc_add, ecc_multiply.

# TODO

- [ ] extract_variable, Add type for parameter sample, dimod.sampleset.Sample
- [ ] Create a method for getting graph of bqm
- [ ] no variable is left on test case (5, 1), test_arithmetic.py test_multiply_const
- [ ] create better error messages
- [ ] create flowchart to reduce number of bits used, ex) when using not_gate, if bit is set to constant use flow to set the other bit as well
- [ ] create a better test for ensure_modulo, current one cannot compare before and after value, maybe use a add first and use ensure modulo
- [ ] better assert method for test_add_modp, replace (0, 0, '000') to (0, 0, '000', '101')
- [ ] create constant class to make it unchangeable
- [ ] calculate the number of input bits, output bits, ancilla bits of each operations.

- [ ] ensure modulo might not be required at the last step of ecc multiply, since setting public key to constant will create a bias similar to ensure modulo
