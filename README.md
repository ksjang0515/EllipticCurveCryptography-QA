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
- [ ] remove zero_gate, one_gate, and set bit to constant
- [ ] create flowchart to reduce number of bits used, ex) when using not_gate, if bit is set to constant use flow to set the other bit as well

1. add_no_overflow, last carry to zero
2.

Warning

1. When merging two bit, a and b, after b has been merged to a since id of a and b is different change in b will not affect a. Consider using merged bit structure or using a dictionary to map Bit's index to actual bit name

Bit.index -> Map -> bit name ??? what happens when merging 3 bits
