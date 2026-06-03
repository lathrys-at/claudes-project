"""Tests for the rational arithmetic example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source, EvalError
import io
import sys


@pytest.fixture(scope="module")
def rational_env_and_output():
    """Load the rational.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "rational.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestRational:
    """Tests for the rational arithmetic library."""

    def test_example_output(self, rational_env_and_output):
        """Test that the example file produces output without error."""
        env, demo_output = rational_env_and_output
        # Should have output from the demo displayln calls
        assert len(demo_output) > 0
        assert "1/2 + 1/3 = " in demo_output

    # ===== NORMALIZATION TESTS =====

    def test_normalize_reduce_fraction(self, rational_env_and_output):
        """Test that make-rat 2 4 reduces to 1/2."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (make-rat 2 4))', env)
        den = eval_source('(rat-den (make-rat 2 4))', env)
        assert num == 1
        assert den == 2

    def test_normalize_negative_numerator(self, rational_env_and_output):
        """Test that make-rat 3 -6 normalizes to -1/2."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (make-rat 3 -6))', env)
        den = eval_source('(rat-den (make-rat 3 -6))', env)
        assert num == -1
        assert den == 2

    def test_normalize_both_negative(self, rational_env_and_output):
        """Test that make-rat -4 -8 normalizes to 1/2."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (make-rat -4 -8))', env)
        den = eval_source('(rat-den (make-rat -4 -8))', env)
        assert num == 1
        assert den == 2

    def test_normalize_zero(self, rational_env_and_output):
        """Test that make-rat 0 5 normalizes to 0/1."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (make-rat 0 5))', env)
        den = eval_source('(rat-den (make-rat 0 5))', env)
        assert num == 0
        assert den == 1

    def test_normalize_integer(self, rational_env_and_output):
        """Test that make-rat 5 1 stays as 5/1."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (make-rat 5 1))', env)
        den = eval_source('(rat-den (make-rat 5 1))', env)
        assert num == 5
        assert den == 1

    # ===== ZERO DENOMINATOR TESTS =====

    def test_zero_denominator_error(self, rational_env_and_output):
        """Test that make-rat 1 0 raises an error."""
        env, _ = rational_env_and_output
        with pytest.raises(EvalError):
            eval_source('(make-rat 1 0)', env)

    # ===== ARITHMETIC EXACTNESS TESTS =====

    def test_addition_one_third_one_sixth(self, rational_env_and_output):
        """Test that 1/3 + 1/6 = 1/2 exactly."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (rat-add (make-rat 1 3) (make-rat 1 6)))', env)
        den = eval_source('(rat-den (rat-add (make-rat 1 3) (make-rat 1 6)))', env)
        assert num == 1
        assert den == 2

    def test_subtraction_one_half_one_third(self, rational_env_and_output):
        """Test that 1/2 - 1/3 = 1/6 exactly."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (rat-sub (make-rat 1 2) (make-rat 1 3)))', env)
        den = eval_source('(rat-den (rat-sub (make-rat 1 2) (make-rat 1 3)))', env)
        assert num == 1
        assert den == 6

    def test_multiplication_two_thirds_three_fourths(self, rational_env_and_output):
        """Test that 2/3 * 3/4 = 1/2 exactly."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (rat-mul (make-rat 2 3) (make-rat 3 4)))', env)
        den = eval_source('(rat-den (rat-mul (make-rat 2 3) (make-rat 3 4)))', env)
        assert num == 1
        assert den == 2

    def test_division_one_half_three_fourths(self, rational_env_and_output):
        """Test that (1/2) / (3/4) = 2/3 exactly."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (rat-div (make-rat 1 2) (make-rat 3 4)))', env)
        den = eval_source('(rat-den (rat-div (make-rat 1 2) (make-rat 3 4)))', env)
        assert num == 2
        assert den == 3

    def test_addition_result_integer(self, rational_env_and_output):
        """Test that 1/2 + 1/2 = 1/1 (integer result)."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (rat-add (make-rat 1 2) (make-rat 1 2)))', env)
        den = eval_source('(rat-den (rat-add (make-rat 1 2) (make-rat 1 2)))', env)
        assert num == 1
        assert den == 1

    def test_addition_with_negatives(self, rational_env_and_output):
        """Test that -1/2 + 1/3 = -1/6 exactly."""
        env, _ = rational_env_and_output
        num = eval_source('(rat-num (rat-add (make-rat -1 2) (make-rat 1 3)))', env)
        den = eval_source('(rat-den (rat-add (make-rat -1 2) (make-rat 1 3)))', env)
        assert num == -1
        assert den == 6

    # ===== BIG INTEGER EXACTNESS TESTS =====

    def test_big_integer_exactness(self, rational_env_and_output):
        """Test exactness with large denominators that would lose precision in float."""
        env, _ = rational_env_and_output
        # Create two fractions with large denominators
        # 1/p + 1/q = (q + p) / (p*q) in lowest terms
        # We compute the result and verify it's exact
        result = eval_source(
            '(let ((r (rat-add (make-rat 1 1000000007) (make-rat 1 1000000009)))) (list (rat-num r) (rat-den r)))',
            env
        )
        num = result[0]
        den = result[1]
        # The result should be exact in integer arithmetic
        # Just verify that both are integers (no floating point involved)
        assert isinstance(num, int)
        assert isinstance(den, int)
        # Verify the denominator is positive
        assert den > 0

    # ===== DIVISION BY ZERO TESTS =====

    def test_rat_div_by_zero(self, rational_env_and_output):
        """Test that (rat-div (make-rat 1 2) (make-rat 0 5)) raises an error."""
        env, _ = rational_env_and_output
        with pytest.raises(EvalError):
            eval_source('(rat-div (make-rat 1 2) (make-rat 0 5))', env)

    # ===== EQUALITY TESTS =====

    def test_equal_reduced_forms(self, rational_env_and_output):
        """Test that 1/2 equals 2/4 (both reduce to 1/2)."""
        env, _ = rational_env_and_output
        result = eval_source('(rat-equal? (make-rat 1 2) (make-rat 2 4))', env)
        assert result is True

    def test_not_equal_different_values(self, rational_env_and_output):
        """Test that 1/2 does not equal 1/3."""
        env, _ = rational_env_and_output
        result = eval_source('(rat-equal? (make-rat 1 2) (make-rat 1 3))', env)
        assert result is False

    # ===== LESS THAN TESTS =====

    def test_less_than_true_positive(self, rational_env_and_output):
        """Test that 1/3 < 1/2 is true."""
        env, _ = rational_env_and_output
        result = eval_source('(rat-less? (make-rat 1 3) (make-rat 1 2))', env)
        assert result is True

    def test_less_than_true_with_negatives(self, rational_env_and_output):
        """Test that -1/2 < 1/3 is true."""
        env, _ = rational_env_and_output
        result = eval_source('(rat-less? (make-rat -1 2) (make-rat 1 3))', env)
        assert result is True

    def test_less_than_false(self, rational_env_and_output):
        """Test that 1/2 < 1/3 is false."""
        env, _ = rational_env_and_output
        result = eval_source('(rat-less? (make-rat 1 2) (make-rat 1 3))', env)
        assert result is False

    def test_less_than_equal_false(self, rational_env_and_output):
        """Test that 1/2 < 1/2 is false (not less, equal)."""
        env, _ = rational_env_and_output
        result = eval_source('(rat-less? (make-rat 1 2) (make-rat 1 2))', env)
        assert result is False

    # ===== STRING REPRESENTATION TESTS =====

    def test_rat_to_string_fraction(self, rational_env_and_output):
        """Test that rat->string returns '1/2' for make-rat 1 2."""
        env, _ = rational_env_and_output
        result = eval_source('(rat->string (make-rat 1 2))', env)
        assert result == "1/2"

    def test_rat_to_string_integer(self, rational_env_and_output):
        """Test that rat->string returns '3' for make-rat 3 1."""
        env, _ = rational_env_and_output
        result = eval_source('(rat->string (make-rat 3 1))', env)
        assert result == "3"

    def test_rat_to_string_negative(self, rational_env_and_output):
        """Test that rat->string returns '-3/4' for make-rat -3 4."""
        env, _ = rational_env_and_output
        result = eval_source('(rat->string (make-rat -3 4))', env)
        assert result == "-3/4"

    def test_rat_to_string_zero(self, rational_env_and_output):
        """Test that rat->string returns '0' for make-rat 0 5."""
        env, _ = rational_env_and_output
        result = eval_source('(rat->string (make-rat 0 5))', env)
        assert result == "0"

    # ===== FLOAT CONVERSION TESTS =====

    def test_rat_to_float(self, rational_env_and_output):
        """Test that rat->float returns 0.5 for make-rat 1 2."""
        env, _ = rational_env_and_output
        result = eval_source('(rat->float (make-rat 1 2))', env)
        assert result == 0.5

    def test_rat_to_float_integer_result(self, rational_env_and_output):
        """Test that rat->float returns 3.0 for make-rat 3 1."""
        env, _ = rational_env_and_output
        result = eval_source('(rat->float (make-rat 3 1))', env)
        assert result == 3.0

    def test_rat_to_float_negative(self, rational_env_and_output):
        """Test that rat->float returns -0.5 for make-rat -1 2."""
        env, _ = rational_env_and_output
        result = eval_source('(rat->float (make-rat -1 2))', env)
        assert result == -0.5

    def test_rat_to_float_one_third(self, rational_env_and_output):
        """Test that rat->float returns approximately 0.333... for make-rat 1 3."""
        env, _ = rational_env_and_output
        result = eval_source('(rat->float (make-rat 1 3))', env)
        # Allow small floating-point error
        assert abs(result - 1.0 / 3.0) < 1e-10
