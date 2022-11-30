Elliptic Curve Cryptography implementation on Dwave's Quantum Annealer

ECC Point multiplication, [Double-and-add](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Double-and-add) method comparison

1. index decreasing

   requires doubling and addition

2. index increasing

   doubles of G can be precomputed, reducing the number of operations

   by subtracting G at the last step, point at infinity(starting point) can be replaced by G

TODO

- [ ] ecc_multiply, Implement subtraction at last step
- [ ] extract_variable, Add type for parameter sample, dimod.sampleset.Sample
- [ ] add_no_overflow, remove carry in last operation`
