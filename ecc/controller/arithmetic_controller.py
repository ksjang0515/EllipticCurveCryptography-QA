
from typing import Optional

from ecc.controller.gate_controller import GateController
from ecc.types import Bit, Binary, Name, Variable, Constant


class ArithmeticController(GateController):
    def __init__(self) -> None:
        super().__init__()

    def add(self, a: Variable, b: Variable, c: Variable) -> None:
        """c = a + b"""
        if not len(c) == max(len(a), len(b)) + 1:
            raise ValueError("C length is too short")

        if len(a) < len(b):
            # swap so var1 is longer than var2
            temp = a
            a = b
            b = temp

        carry: Bit = self.get_bit()
        self.halfadder_gate(a[0], b[0], c[0], carry)

        for i in range(1, len(b)):
            pre_carry = carry
            carry = self.get_bit()
            self.fulladder_gate(a[i], b[i], pre_carry, c[i], carry)

        if len(a) == len(b):
            self.merge_bit(c[-1], carry)
            return

        for i in range(len(b), len(a)):
            pre_carry = carry
            carry = self.get_bit()
            self.halfadder_gate(a[i], pre_carry, c[i], carry)

        self.merge_bit(c[-1], carry)

    def add_no_overflow(self, a: Variable, b: Variable, c: Variable) -> None:
        """c = a + b (no last carry), don't use if a+b could be larger than c's maximum value"""

        if not len(c) == max(len(a), len(b)):
            raise ValueError("C length is too short")

        ancilla = self.get_bit()
        c_ = [*c, ancilla]

        self.add(a, b, c_)
        self.zero_gate(ancilla)

    def add_const(self, a: Variable, b: Constant, c: Variable) -> None:
        """c = a + b(constant)"""
        b = self.check_ConstantType(b)

        if len(a) < len(b):
            raise ValueError("B cannot be longer than A")

        if not len(c) == len(a) + 1:
            raise ValueError("C length is too short")

        carry: Optional[Bit] = None
        for i in range(len(b)):
            if carry != None:
                pre_carry = carry
                carry, sum_, ancilla = self.get_bit(3)

                self.fulladder_gate(a[i], ancilla, pre_carry, sum_, carry)
                self.set_bit_constant(ancilla, b[i])

            else:
                if b[i] == 1:
                    sum_ = self.get_bit()
                    carry = a[i]

                    self.not_gate(a[i], sum_)

                else:
                    sum_ = a[i]

            self.merge_bit(c[i], sum_)

        if len(a) == len(b):
            if carry == None:
                self.zero_gate(c[-1])
                return

            self.merge_bit(c[-1], carry)
            return

        if not carry:
            self.merge_variable(c[len(b): len(a)], a[len(b): len(a)])

            self.zero_gate(c[-1])
            return

        for i in range(len(b), len(a)):
            pre_carry = carry
            carry, sum_ = self.get_bit(2)

            self.halfadder_gate(a[i], pre_carry, sum_, carry)
            self.merge_bit(c[i], sum_)

        self.merge_bit(c[-1], carry)

    def subtract(self, a: Variable, b: Variable, c: Variable, underflow: Bit):
        """c = a - b"""

        if not (len(c) == len(a) == len(b)):
            raise ValueError("A, B, C length must be same")

        var_ = [*a, underflow]

        self.add(b, c, var_)

    def subtract_const(self, a: Variable, b: Constant, c: Variable, underflow: Bit) -> None:
        """c = a - b"""

        if len(c) != len(a):
            raise ValueError("A, C length must be same")

        var_ = [*a, underflow]

        self.add_const(c, b, var_)

    def multiply(self, a: Variable, b: Variable, c: Variable) -> None:
        """c = a * b"""

        a_length = len(a)  # n
        b_length = len(b)  # n2
        c_length = len(c)

        if a_length + b_length != c_length and a_length * b_length != c_length:
            raise ValueError("C length is too short")

        ctrl_ancilla_var = self.get_bit(a_length)
        self.ctrl_var(b[0], a, ctrl_ancilla_var)

        self.merge_bit(c[0], ctrl_ancilla_var[0])
        pre_add_ancilla_var = ctrl_ancilla_var[1:]  # n-1

        for i in range(1, b_length):
            ctrl_ancilla_var = self.get_bit(a_length)  # n
            self.ctrl_var(b[i], a, ctrl_ancilla_var)

            # n+1 (n+n => n+1 or n-1+n => n+1)
            add_ancilla_var = self.get_bit(a_length+1)
            self.add(pre_add_ancilla_var, ctrl_ancilla_var, add_ancilla_var)

            self.merge_bit(c[i], add_ancilla_var[0])
            pre_add_ancilla_var = add_ancilla_var[1:]  # n

        self.merge_variable(c[b_length:c_length], pre_add_ancilla_var)

    def multiply_const(self, a: Variable, b: Constant, c: Variable) -> None:
        """c = a * b"""

        a_length = len(a)
        b_length = len(b)
        c_length = len(c)

        if a_length + b_length != c_length and a_length * b_length != c_length:
            raise ValueError("C length is too short")

        pre_add_ancilla_var = []
        for i in range(b_length):
            if pre_add_ancilla_var:
                if b[i] == 1:
                    add_ancilla_var = self.get_bit(a_length + 1)
                    self.add(a, pre_add_ancilla_var, add_ancilla_var)

                    self.merge_bit(c[i], add_ancilla_var[0])
                    pre_add_ancilla_var = add_ancilla_var[1:]

                else:
                    self.merge_bit(c[i], pre_add_ancilla_var[0])
                    pre_add_ancilla_var = pre_add_ancilla_var[1:]

            else:
                if b[i] == 1:
                    ctrl_ancilla_var = a[:]

                    self.merge_bit(c[i], ctrl_ancilla_var[0])
                    pre_add_ancilla_var = ctrl_ancilla_var[1:]

                else:
                    self.zero_gate(c[i])

        self.merge_variable(
            c[b_length:b_length+len(pre_add_ancilla_var)], pre_add_ancilla_var)

        current = b_length + len(pre_add_ancilla_var)
        if current == len(c):
            return

        for i in range(current, len(c)):
            self.zero_gate(c[i])

    def square(self, a: Variable, c: Variable) -> None:
        """c = a^2"""

        def ctrl_skip_var(var, index, out):
            for i in range(len(var)):
                if i == index:
                    out[i] = var[i]
                    continue

                self.and_gate(var[i], var[index], out[i])

        var_length = len(a)  # n

        if 2 * var_length != len(c):
            raise ValueError("C length is too short")

        ctrl_ancilla_var = self.get_bit(var_length)
        ctrl_skip_var(a, 0, ctrl_ancilla_var)

        pre_add_ancilla_var = ctrl_ancilla_var[1:]  # n-1
        self.merge_bit(c[0], ctrl_ancilla_var[0])

        for i in range(1, var_length):
            ctrl_ancilla_var = self.get_bit(var_length)  # n
            ctrl_skip_var(a, i, ctrl_ancilla_var)

            # n+1 (n+n => n+1 or n-1+n => n+1)
            add_ancilla_var = self.get_bit(var_length + 1)
            self.add(pre_add_ancilla_var, ctrl_ancilla_var, add_ancilla_var)

            pre_add_ancilla_var = add_ancilla_var[1:]  # n
            self.merge_bit(c[i], add_ancilla_var[0])

        # (n + n2) - n2 = n

        self.merge_variable(c[var_length:], pre_add_ancilla_var)
