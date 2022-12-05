import ecc

controller = ecc.GateController()
a, b, c, d, e, f = controller.get_bit(6)

controller.and_gate(a, b, c)
controller.or_gate(d, e, f)

controller.merge_bit(c, f)

solution = controller.run_ExactSolver()
lowest = solution.lowest()

a_, b_, c_, d_, e_, f_ = controller.get_names(a, b, c, d, e, f)
print(f'a-{a_} b-{b_} c-{c_} d-{d_} e-{e_} f-{f_}')
print(lowest)
