"""Tests for numeric builtins: quotient, remainder, gcd, lcm, sqrt, floor, ceiling, round, truncate."""

import pytest
import math
from pebble.evaluator import make_global_env, eval_source, EvalError


def eval_pebble(source):
    """Helper to evaluate Pebble source and return result."""
    env = make_global_env()
    return eval_source(source, env)


class TestQuotient:
    """Tests for quotient (integer division truncated toward zero)."""

    def test_quotient_positive(self):
        """quotient with positive operands."""
        assert eval_pebble("(quotient 7 2)") == 3
        assert eval_pebble("(quotient 8 2)") == 4
        assert eval_pebble("(quotient 5 3)") == 1

    def test_quotient_negative_dividend(self):
        """quotient with negative dividend."""
        assert eval_pebble("(quotient -7 2)") == -3

    def test_quotient_negative_divisor(self):
        """quotient with negative divisor."""
        assert eval_pebble("(quotient 7 -2)") == -3

    def test_quotient_both_negative(self):
        """quotient with both operands negative."""
        assert eval_pebble("(quotient -7 -2)") == 3

    def test_quotient_identity(self):
        """Verify a == b*(quotient a b) + (remainder a b)."""

        def check_identity(a, b):
            expr = f"(+ (* {b} (quotient {a} {b})) (remainder {a} {b}))"
            result = eval_pebble(expr)
            assert result == a, f"Identity failed for {a}, {b}: got {result}"

        check_identity(7, 2)
        check_identity(-7, 2)
        check_identity(7, -2)
        check_identity(-7, -2)

    def test_quotient_division_by_zero(self):
        """quotient with zero divisor raises EvalError."""
        with pytest.raises(EvalError, match="division by zero"):
            eval_pebble("(quotient 7 0)")

    def test_quotient_non_integer_first_arg(self):
        """quotient with non-integer first argument raises EvalError."""
        with pytest.raises(EvalError, match="first argument must be an integer"):
            eval_pebble("(quotient 1.5 2)")

    def test_quotient_non_integer_second_arg(self):
        """quotient with non-integer second argument raises EvalError."""
        with pytest.raises(EvalError, match="second argument must be an integer"):
            eval_pebble("(quotient 7 2.5)")

    def test_quotient_boolean_arg(self):
        """quotient with boolean argument raises EvalError."""
        with pytest.raises(EvalError, match="first argument must be an integer"):
            eval_pebble("(quotient true 2)")
        with pytest.raises(EvalError, match="second argument must be an integer"):
            eval_pebble("(quotient 7 false)")


class TestRemainder:
    """Tests for remainder (remainder of truncating division, sign follows dividend)."""

    def test_remainder_positive(self):
        """remainder with positive operands."""
        assert eval_pebble("(remainder 7 2)") == 1

    def test_remainder_negative_dividend(self):
        """remainder with negative dividend (sign follows dividend)."""
        assert eval_pebble("(remainder -7 2)") == -1

    def test_remainder_negative_divisor(self):
        """remainder with negative divisor (sign follows dividend)."""
        assert eval_pebble("(remainder 7 -2)") == 1

    def test_remainder_both_negative(self):
        """remainder with both operands negative."""
        assert eval_pebble("(remainder -7 -2)") == -1

    def test_modulo_vs_remainder_distinction(self):
        """Show the difference between modulo and remainder for negative dividend."""
        # (modulo -7 2) should be 1 (sign follows divisor)
        assert eval_pebble("(modulo -7 2)") == 1
        # (remainder -7 2) should be -1 (sign follows dividend)
        assert eval_pebble("(remainder -7 2)") == -1

    def test_remainder_division_by_zero(self):
        """remainder with zero divisor raises EvalError."""
        with pytest.raises(EvalError, match="division by zero"):
            eval_pebble("(remainder 7 0)")

    def test_remainder_non_integer_first_arg(self):
        """remainder with non-integer first argument raises EvalError."""
        with pytest.raises(EvalError, match="first argument must be an integer"):
            eval_pebble("(remainder 1.5 2)")

    def test_remainder_non_integer_second_arg(self):
        """remainder with non-integer second argument raises EvalError."""
        with pytest.raises(EvalError, match="second argument must be an integer"):
            eval_pebble("(remainder 7 2.5)")

    def test_remainder_boolean_arg(self):
        """remainder with boolean argument raises EvalError."""
        with pytest.raises(EvalError, match="first argument must be an integer"):
            eval_pebble("(remainder true 2)")
        with pytest.raises(EvalError, match="second argument must be an integer"):
            eval_pebble("(remainder 7 false)")


class TestGcd:
    """Tests for greatest common divisor (variadic, sign-independent)."""

    def test_gcd_no_args(self):
        """gcd with no arguments returns 0."""
        assert eval_pebble("(gcd)") == 0

    def test_gcd_single_arg(self):
        """gcd with single argument returns absolute value."""
        assert eval_pebble("(gcd 5)") == 5
        assert eval_pebble("(gcd -5)") == 5

    def test_gcd_two_args(self):
        """gcd with two arguments."""
        assert eval_pebble("(gcd -12 18)") == 6
        assert eval_pebble("(gcd 12 18)") == 6
        assert eval_pebble("(gcd 18 12)") == 6

    def test_gcd_three_args(self):
        """gcd with three arguments."""
        assert eval_pebble("(gcd 12 18 24)") == 6

    def test_gcd_with_zero(self):
        """gcd with zero."""
        assert eval_pebble("(gcd 0 5)") == 5
        assert eval_pebble("(gcd 5 0)") == 5
        assert eval_pebble("(gcd 0 0)") == 0

    def test_gcd_non_integer_arg(self):
        """gcd with non-integer argument raises EvalError."""
        with pytest.raises(EvalError, match="all arguments must be integers"):
            eval_pebble("(gcd 1.5 2)")

    def test_gcd_boolean_arg(self):
        """gcd with boolean argument raises EvalError."""
        with pytest.raises(EvalError, match="all arguments must be integers"):
            eval_pebble("(gcd true 2)")


class TestLcm:
    """Tests for least common multiple (variadic, sign-independent)."""

    def test_lcm_no_args(self):
        """lcm with no arguments returns 1."""
        assert eval_pebble("(lcm)") == 1

    def test_lcm_single_arg(self):
        """lcm with single argument returns absolute value."""
        assert eval_pebble("(lcm 5)") == 5
        assert eval_pebble("(lcm -5)") == 5

    def test_lcm_two_args(self):
        """lcm with two arguments."""
        assert eval_pebble("(lcm 4 6)") == 12

    def test_lcm_with_zero(self):
        """lcm with zero returns 0."""
        assert eval_pebble("(lcm 0 5)") == 0
        assert eval_pebble("(lcm 5 0)") == 0

    def test_lcm_three_args(self):
        """lcm with three arguments."""
        assert eval_pebble("(lcm 2 3 4)") == 12

    def test_lcm_negative_args(self):
        """lcm ignores sign."""
        assert eval_pebble("(lcm -4 6)") == 12

    def test_lcm_non_integer_arg(self):
        """lcm with non-integer argument raises EvalError."""
        with pytest.raises(EvalError, match="all arguments must be integers"):
            eval_pebble("(lcm 1.5 2)")

    def test_lcm_boolean_arg(self):
        """lcm with boolean argument raises EvalError."""
        with pytest.raises(EvalError, match="all arguments must be integers"):
            eval_pebble("(lcm true 2)")


class TestSqrt:
    """Tests for square root (returns float)."""

    def test_sqrt_perfect_square_int(self):
        """sqrt of perfect square integer."""
        result = eval_pebble("(sqrt 4)")
        assert isinstance(result, float)
        assert result == 2.0

    def test_sqrt_perfect_square_float(self):
        """sqrt of perfect square float."""
        result = eval_pebble("(sqrt 9.0)")
        assert isinstance(result, float)
        assert result == 3.0

    def test_sqrt_irrational(self):
        """sqrt of irrational number."""
        result = eval_pebble("(sqrt 2)")
        assert isinstance(result, float)
        assert abs(result - math.sqrt(2)) < 1e-10

    def test_sqrt_zero(self):
        """sqrt of zero."""
        result = eval_pebble("(sqrt 0)")
        assert result == 0.0

    def test_sqrt_one(self):
        """sqrt of one."""
        result = eval_pebble("(sqrt 1)")
        assert result == 1.0

    def test_sqrt_negative_raises_error(self):
        """sqrt of negative raises EvalError."""
        with pytest.raises(EvalError, match="cannot take square root of negative"):
            eval_pebble("(sqrt -1)")

    def test_sqrt_non_number_arg(self):
        """sqrt with non-number argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(sqrt \"x\")")

    def test_sqrt_boolean_arg(self):
        """sqrt with boolean argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(sqrt true)")


class TestFloor:
    """Tests for floor (largest integer <= x, returns int)."""

    def test_floor_positive_float(self):
        """floor of positive float."""
        result = eval_pebble("(floor 3.7)")
        assert result == 3
        assert isinstance(result, int)

    def test_floor_negative_float(self):
        """floor of negative float."""
        result = eval_pebble("(floor -3.2)")
        assert result == -4
        assert isinstance(result, int)

    def test_floor_integer(self):
        """floor of integer."""
        result = eval_pebble("(floor 5)")
        assert result == 5
        assert isinstance(result, int)

    def test_floor_zero(self):
        """floor of zero."""
        result = eval_pebble("(floor 0)")
        assert result == 0

    def test_floor_non_number_arg(self):
        """floor with non-number argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(floor \"x\")")

    def test_floor_boolean_arg(self):
        """floor with boolean argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(floor true)")


class TestCeiling:
    """Tests for ceiling (smallest integer >= x, returns int)."""

    def test_ceiling_positive_float(self):
        """ceiling of positive float."""
        result = eval_pebble("(ceiling 3.2)")
        assert result == 4
        assert isinstance(result, int)

    def test_ceiling_negative_float(self):
        """ceiling of negative float."""
        result = eval_pebble("(ceiling -3.7)")
        assert result == -3
        assert isinstance(result, int)

    def test_ceiling_integer(self):
        """ceiling of integer."""
        result = eval_pebble("(ceiling 5)")
        assert result == 5
        assert isinstance(result, int)

    def test_ceiling_zero(self):
        """ceiling of zero."""
        result = eval_pebble("(ceiling 0)")
        assert result == 0

    def test_ceiling_non_number_arg(self):
        """ceiling with non-number argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(ceiling \"x\")")

    def test_ceiling_boolean_arg(self):
        """ceiling with boolean argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(ceiling true)")


class TestRound:
    """Tests for round (nearest integer, banker's rounding, returns int)."""

    def test_round_half_to_even_2_5(self):
        """round 2.5 to even -> 2."""
        result = eval_pebble("(round 2.5)")
        assert result == 2
        assert isinstance(result, int)

    def test_round_half_to_even_3_5(self):
        """round 3.5 to even -> 4."""
        result = eval_pebble("(round 3.5)")
        assert result == 4
        assert isinstance(result, int)

    def test_round_below_half(self):
        """round 2.4 -> 2."""
        result = eval_pebble("(round 2.4)")
        assert result == 2

    def test_round_above_half(self):
        """round 2.6 -> 3."""
        result = eval_pebble("(round 2.6)")
        assert result == 3

    def test_round_negative(self):
        """round negative float."""
        result = eval_pebble("(round -2.5)")
        assert result == -2

    def test_round_integer(self):
        """round of integer."""
        result = eval_pebble("(round 5)")
        assert result == 5
        assert isinstance(result, int)

    def test_round_zero(self):
        """round of zero."""
        result = eval_pebble("(round 0)")
        assert result == 0

    def test_round_non_number_arg(self):
        """round with non-number argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(round \"x\")")

    def test_round_boolean_arg(self):
        """round with boolean argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(round true)")


class TestTruncate:
    """Tests for truncate (integer part toward zero, returns int)."""

    def test_truncate_positive_float(self):
        """truncate of positive float."""
        result = eval_pebble("(truncate 3.7)")
        assert result == 3
        assert isinstance(result, int)

    def test_truncate_negative_float(self):
        """truncate of negative float."""
        result = eval_pebble("(truncate -3.7)")
        assert result == -3
        assert isinstance(result, int)

    def test_truncate_integer(self):
        """truncate of integer."""
        result = eval_pebble("(truncate 5)")
        assert result == 5
        assert isinstance(result, int)

    def test_truncate_zero(self):
        """truncate of zero."""
        result = eval_pebble("(truncate 0)")
        assert result == 0

    def test_truncate_non_number_arg(self):
        """truncate with non-number argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(truncate \"x\")")

    def test_truncate_boolean_arg(self):
        """truncate with boolean argument raises EvalError."""
        with pytest.raises(EvalError, match="argument must be a number"):
            eval_pebble("(truncate true)")


class TestTypeErrors:
    """Tests for type errors across numeric functions."""

    def test_quotient_string_arg(self):
        """quotient with string argument."""
        with pytest.raises(EvalError):
            eval_pebble("(quotient \"x\" 2)")

    def test_gcd_string_arg(self):
        """gcd with string argument."""
        with pytest.raises(EvalError):
            eval_pebble("(gcd \"x\" 2)")

    def test_lcm_float_arg(self):
        """lcm with float argument."""
        with pytest.raises(EvalError):
            eval_pebble("(lcm 1.5 2)")

    def test_sqrt_list_arg(self):
        """sqrt with list argument."""
        with pytest.raises(EvalError):
            eval_pebble("(sqrt (list 1 2))")
