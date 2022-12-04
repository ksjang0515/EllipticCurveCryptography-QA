# Elliptic Curve Cryptography Implementation using Dwave's Ocean SDK

### ECC Point multiplication, [Double-and-add](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Double-and-add) method comparison

1. Index Decreasing

   requires doubling and addition

2. Index Increasing

   doubles of G can be precomputed, reducing the number of operations

   by subtracting G at the last step, point at infinity(starting point) can be replaced by G

---

TODO

- [ ] extract_variable, Add type for parameter sample, dimod.sampleset.Sample
- [ ] Create a method for getting graph of bqm
- [ ] Make sure set_variable is done at the end, because dimod removes the variable when using fix_variable
- [ ] no variable is left on test case (5, 1), test_arithmetic.py test_multiply_const
- [ ] show current variable length for length related ValueErrors in Controller
