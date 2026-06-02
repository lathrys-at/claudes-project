"""Tests for bitwise integer operation builtins."""
import pytest
from pebble.evaluator import make_global_env, seval, EvalError
from pebble.reader import read_one


def eval_expr(env, code):
    """Helper to evaluate Pebble source code."""
    expr = read_one(code)
    return seval(expr, env)


class TestBitAnd:
    """Tests for bit-and builtin."""

    def test_bit_and_no_args(self):
        """(bit-and) -> -1 (identity)."""
        env = make_global_env()
        result = eval_expr(env, "(bit-and)")
        assert result == -1

    def test_bit_and_two_args(self):
        """(bit-and 12 10) -> 8."""
        env = make_global_env()
        result = eval_expr(env, "(bit-and 12 10)")
        assert result == 8

    def test_bit_and_three_args(self):
        """(bit-and 12 10 6) -> 0."""
        env = make_global_env()
        result = eval_expr(env, "(bit-and 12 10 6)")
        assert result == 0

    def test_bit_and_float_arg(self):
        """bit-and with float argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(bit-and 1.5 2)")

    def test_bit_and_boolean_arg(self):
        """bit-and with boolean argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(bit-and true 1)")

    def test_bit_and_string_arg(self):
        """bit-and with string argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, '(bit-and "x" 1)')


class TestBitOr:
    """Tests for bit-or builtin."""

    def test_bit_or_no_args(self):
        """(bit-or) -> 0 (identity)."""
        env = make_global_env()
        result = eval_expr(env, "(bit-or)")
        assert result == 0

    def test_bit_or_two_args(self):
        """(bit-or 12 10) -> 14."""
        env = make_global_env()
        result = eval_expr(env, "(bit-or 12 10)")
        assert result == 14

    def test_bit_or_three_args(self):
        """(bit-or 1 2 4) -> 7."""
        env = make_global_env()
        result = eval_expr(env, "(bit-or 1 2 4)")
        assert result == 7

    def test_bit_or_float_arg(self):
        """bit-or with float argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(bit-or 1.5 2)")

    def test_bit_or_boolean_arg(self):
        """bit-or with boolean argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(bit-or true 1)")

    def test_bit_or_string_arg(self):
        """bit-or with string argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, '(bit-or "x" 1)')


class TestBitXor:
    """Tests for bit-xor builtin."""

    def test_bit_xor_no_args(self):
        """(bit-xor) -> 0 (identity)."""
        env = make_global_env()
        result = eval_expr(env, "(bit-xor)")
        assert result == 0

    def test_bit_xor_two_args(self):
        """(bit-xor 12 10) -> 6."""
        env = make_global_env()
        result = eval_expr(env, "(bit-xor 12 10)")
        assert result == 6

    def test_bit_xor_three_args(self):
        """(bit-xor 5 3 1) -> 7."""
        env = make_global_env()
        result = eval_expr(env, "(bit-xor 5 3 1)")
        assert result == 7

    def test_bit_xor_float_arg(self):
        """bit-xor with float argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(bit-xor 1.5 2)")

    def test_bit_xor_boolean_arg(self):
        """bit-xor with boolean argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(bit-xor true 1)")

    def test_bit_xor_string_arg(self):
        """bit-xor with string argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, '(bit-xor "x" 1)')


class TestBitNot:
    """Tests for bit-not builtin."""

    def test_bit_not_zero(self):
        """(bit-not 0) -> -1."""
        env = make_global_env()
        result = eval_expr(env, "(bit-not 0)")
        assert result == -1

    def test_bit_not_positive(self):
        """(bit-not 5) -> -6."""
        env = make_global_env()
        result = eval_expr(env, "(bit-not 5)")
        assert result == -6

    def test_bit_not_negative(self):
        """(bit-not -1) -> 0."""
        env = make_global_env()
        result = eval_expr(env, "(bit-not -1)")
        assert result == 0

    def test_bit_not_float_arg(self):
        """bit-not with float argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(bit-not 1.5)")

    def test_bit_not_boolean_arg(self):
        """bit-not with boolean argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(bit-not true)")

    def test_bit_not_string_arg(self):
        """bit-not with string argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, '(bit-not "x")')


class TestArithmeticShift:
    """Tests for arithmetic-shift builtin."""

    def test_arithmetic_shift_left(self):
        """(arithmetic-shift 1 4) -> 16 (left shift)."""
        env = make_global_env()
        result = eval_expr(env, "(arithmetic-shift 1 4)")
        assert result == 16

    def test_arithmetic_shift_right_positive(self):
        """(arithmetic-shift 255 -4) -> 15 (right shift positive)."""
        env = make_global_env()
        result = eval_expr(env, "(arithmetic-shift 255 -4)")
        assert result == 15

    def test_arithmetic_shift_right_negative(self):
        """(arithmetic-shift -8 -1) -> -4 (arithmetic right shift preserves sign)."""
        env = make_global_env()
        result = eval_expr(env, "(arithmetic-shift -8 -1)")
        assert result == -4

    def test_arithmetic_shift_zero(self):
        """(arithmetic-shift 3 0) -> 3 (shift by zero)."""
        env = make_global_env()
        result = eval_expr(env, "(arithmetic-shift 3 0)")
        assert result == 3

    def test_arithmetic_shift_first_arg_float(self):
        """arithmetic-shift with float first argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(arithmetic-shift 1.5 2)")

    def test_arithmetic_shift_second_arg_float(self):
        """arithmetic-shift with float second argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(arithmetic-shift 1 1.5)")

    def test_arithmetic_shift_first_arg_boolean(self):
        """arithmetic-shift with boolean first argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(arithmetic-shift true 2)")

    def test_arithmetic_shift_second_arg_boolean(self):
        """arithmetic-shift with boolean second argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, "(arithmetic-shift 1 true)")

    def test_arithmetic_shift_string_arg(self):
        """arithmetic-shift with string argument raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            eval_expr(env, '(arithmetic-shift "x" 2)')

    def test_arithmetic_shift_negative_right_shift_large(self):
        """(arithmetic-shift -1 -1) -> -1 (all bits set)."""
        env = make_global_env()
        result = eval_expr(env, "(arithmetic-shift -1 -1)")
        assert result == -1

    def test_arithmetic_shift_large_left(self):
        """(arithmetic-shift 2 30) -> 2147483648."""
        env = make_global_env()
        result = eval_expr(env, "(arithmetic-shift 2 30)")
        assert result == 2147483648
