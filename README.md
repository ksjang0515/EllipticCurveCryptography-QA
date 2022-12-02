# Elliptic Curve Cryptography Implementation using Dwave's Ocean SDK

### ECC Point multiplication, [Double-and-add](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Double-and-add) method comparison

1. Index Decreasing

   requires doubling and addition

2. Index Increasing

   doubles of G can be precomputed, reducing the number of operations

   by subtracting G at the last step, point at infinity(starting point) can be replaced by G

---

TODO

- [x] ecc_multiply, Implement subtraction at last step
- [ ] extract_variable, Add type for parameter sample, dimod.sampleset.Sample
- [ ] add_no_overflow, remove carry in last operation
- [ ] Create a method for getting graph of bqm
- [ ] Make sure set_variable is done at the end, because dimod removes the variable when using fix_variable
- [ ] add test case for ctrl_select_variable, ctrl_var
