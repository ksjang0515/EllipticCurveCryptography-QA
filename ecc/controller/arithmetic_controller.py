import warnings

from ecc.controller.gate_controller import GateController
from ecc.types import VariableType, ConstantType, Bit


class ArithmeticController(GateController):
    def __init__(self) -> None:
        super().__init__()

    def add(
        self, A: VariableType, B: VariableType, C: VariableType
    ) -> None:
        """C = A + B"""
        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        if not len(c) == max(len(a), len(b)) + 1:
            raise ValueError("out Variable length is too short")

        if len(a) < len(b):
            # swap so var1 is longer than var2
            temp = a
            a = b
            b = temp

        carry = self.get_bit()
        self.halfadder_gate(a[0], b[0], c[0], carry)

        for i in range(1, len(b)):
            pre_carry = carry
            carry = self.get_bit()
            self.fulladder_gate(a[i], b[i], pre_carry, c[i], carry)

        if len(a) == len(b):
            c[-1].index = carry.index
            return

        for i in range(len(b), len(a)):
            pre_carry = carry
            carry = self.get_bit()
            self.halfadder_gate(a[i], pre_carry, c[i], carry)
        c[-1].index = carry.index

    def add_no_overflow(
        self, A: VariableType, B: VariableType, C: VariableType
    ) -> None:
        """C = A + B (no last carry)"""
        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        if not len(c) == max(len(a), len(b)):
            raise ValueError("out Variable length is too short")

        if len(a) < len(b):
            # swap so var1 is longer than var2
            temp = a
            a = b
            b = temp

        carry = self.get_bit()
        self.halfadder_gate(a[0], b[0], c[0], carry)

        for i in range(1, len(b)):
            pre_carry = carry
            carry = self.get_bit()
            self.fulladder_gate(a[i], b[i], pre_carry, c[i], carry)

        if len(a) == len(b):
            return

        for i in range(len(b), len(a)):
            pre_carry = carry
            carry = self.get_bit()
            self.halfadder_gate(a[i], pre_carry, c[i], carry)

    def add_const(
        self, A: VariableType, B: ConstantType, C: VariableType
    ) -> None:
        """C = A + B
        requires less bit if B is power of 2, but if B is odd number
        this requires more bits than using add method because xor uses one ancilla bit"""

        warnings.warn(
            "add_const method is less efficient than plain add method if constant is odd number")

        a = self.check_VariableType(A)
        b = self.check_ConstantType(B)
        c = self.check_VariableType(C)

        if len(a) < len(b):
            raise ValueError("constant cannot be longer than variable")

        if not len(c) == len(a) + 1:
            raise ValueError("out Variable length is too short")

        carry = None
        for i in range(len(b)):
            if carry:
                pre_carry = carry
                carry = self.get_bit()
                sum_ = self.get_bit()

                if b[i] == 1:
                    self.xnor_gate(a[i], pre_carry, sum_)
                    self.or_gate(a[i], pre_carry, carry)

                else:
                    self.xor_gate(a[i], pre_carry, sum_)
                    self.and_gate(a[i], pre_carry, carry)
            else:
                if b[i] == 1:
                    sum_ = self.get_bit()
                    carry = a[i]

                    self.not_gate(a[i], sum_)

                else:
                    sum_ = a[i]

            c[i].index = sum_.index

        if len(a) == len(carry):
            c[-1].index = carry.index
            return

        if not carry:
            for i in range(len(b), len(a)):
                c[i].index = a[i].index

            zero = self.get_bit()
            self.zero_gate(zero)
            c[-1].index = zero.index

            return

        for i in range(len(b), len(a)):
            pre_carry = carry
            carry = self.get_bit()
            sum_ = self.get_bit()

            self.halfadder_gate(a[i], pre_carry, sum_, carry)

            c[i].index = sum_.index

        c[-1].index = carry.index

    def subtract(
        self,
        A: VariableType,
        B: VariableType,
        C: VariableType,
        underflow: Bit,
    ):
        """C = A - B"""
        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        if not (len(c) == len(a) == len(b)):
            raise ValueError(
                "variable1, variable2, output length must be same")

        var_ = [*a, underflow]

        self.add(b, c, var_)

    def multiply(
        self, A: VariableType, B: VariableType, C: VariableType
    ) -> None:
        """C = A * B"""
        a = self.check_VariableType(A)
        b = self.check_VariableType(B)
        c = self.check_VariableType(C)

        var1_length = len(a)  # n
        var2_length = len(b)  # n2
        out_length = len(c)

        if (
            var1_length + var2_length != out_length
            and var1_length * var2_length
            != out_length  # case where one of variables' length is one
        ):
            raise ValueError("out Variable length is too short")

        ctrl_ancilla_var = self.get_bits(var1_length)
        self.ctrl_var(b[0], a, ctrl_ancilla_var)

        pre_add_ancilla_var = ctrl_ancilla_var[1:]  # n-1
        c[0].index = ctrl_ancilla_var[0].index

        for i in range(1, var2_length):
            ctrl_ancilla_var = self.get_bits(var1_length)  # n
            self.ctrl_var(b[i], a, ctrl_ancilla_var)

            # n+1 (n+n => n+1 or n-1+n => n+1)
            add_ancilla_var = self.get_bits(var1_length + 1)
            self.add(pre_add_ancilla_var, ctrl_ancilla_var, add_ancilla_var)

            pre_add_ancilla_var = add_ancilla_var[1:]  # n
            c[i].index = add_ancilla_var[0].index

        # (n + n2) - n2 = n
        for i in range(len(pre_add_ancilla_var)):
            c[var2_length + i].index = pre_add_ancilla_var[i].index

    def multiply_const(
        self, A: VariableType, B: ConstantType, C: VariableType
    ) -> None:
        """C = A * B
        Unlike add_const method, multiply_const requires less bits because this doesn't use any xor_gate"""
        a = self.check_VariableType(A)
        b = self.check_ConstantType(B)
        c = self.check_VariableType(C)

        var_length = len(a)
        const_length = len(b)

        if var_length + const_length != len(c) and var_length * const_length == len(
            c
        ):
            raise ValueError("out Variable length is too short")

        pre_add_ancilla_var = []
        for i in range(const_length):
            if pre_add_ancilla_var:
                if b[i] == 1:
                    add_ancilla_var = self.get_bits(var_length + 1)
                    self.add(a, pre_add_ancilla_var, add_ancilla_var)
                    c[i].index = add_ancilla_var[0].index
                    pre_add_ancilla_var = add_ancilla_var[1:]

                else:
                    c[i].index = pre_add_ancilla_var[0].index
                    pre_add_ancilla_var = pre_add_ancilla_var[1:]

            else:
                if b[i] == 1:
                    ctrl_ancilla_var = a[:]
                    c[i].index = ctrl_ancilla_var[0].index
                    pre_add_ancilla_var = ctrl_ancilla_var[1:]

                else:
                    c[i].index = self.get_zero_bit().index

        for i in range(len(pre_add_ancilla_var)):
            c[const_length + i].index = pre_add_ancilla_var[i].index

        current = const_length + len(pre_add_ancilla_var)
        if current == len(c):
            return

        for i in range(current, len(c)):
            c[i].index = self.get_zero_bit().index

    def square(self, A: VariableType, C: VariableType) -> None:
        """C = A^2"""
        def ctrl_skip_var(var, index, out):
            for i in range(len(var)):
                if i == index:
                    out[i].index = var[i].index
                    continue

                self.and_gate(var[i], var[index], out[i])

        a = self.check_VariableType(A)
        c = self.check_VariableType(C)

        var_length = len(a)  # n

        if 2 * var_length != len(c):
            raise ValueError("out Variable length is too short")

        ctrl_ancilla_var = self.get_bits(var_length)
        ctrl_skip_var(a, 0, ctrl_ancilla_var)

        pre_add_ancilla_var = ctrl_ancilla_var[1:]  # n-1
        c[0].index = ctrl_ancilla_var[0].index

        for i in range(1, var_length):
            ctrl_ancilla_var = self.get_bits(var_length)  # n
            ctrl_skip_var(a, i, ctrl_ancilla_var)

            # n+1 (n+n => n+1 or n-1+n => n+1)
            add_ancilla_var = self.get_bits(var_length + 1)
            self.add(pre_add_ancilla_var, ctrl_ancilla_var, add_ancilla_var)

            pre_add_ancilla_var = add_ancilla_var[1:]  # n
            c[i].index = add_ancilla_var[0].index

        # (n + n2) - n2 = n
        for i in range(len(pre_add_ancilla_var)):
            c[var_length + i].index = pre_add_ancilla_var[i].index
