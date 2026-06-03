"""Tests for digit manipulation functions: digits, digit-sum, digital-root."""
import pytest
from pebble.evaluator import make_global_env, eval_source, EvalError
from pebble.reader import read_one
from pebble.types import PebbleList


def eval_in_env(source):
    """Evaluate a Pebble expression and return the result."""
    env = make_global_env()
    return eval_source(source, env)


class TestDigits:
    """Test digits function."""

    def test_digits_zero(self):
        """digits(0) should return (0)."""
        result = eval_in_env("(digits 0)")
        expected = PebbleList([0])
        assert result == expected

    def test_digits_single_digit(self):
        """digits(7) should return (7)."""
        result = eval_in_env("(digits 7)")
        expected = PebbleList([7])
        assert result == expected

    def test_digits_two_digits(self):
        """digits(12) should return (1 2)."""
        result = eval_in_env("(digits 12)")
        expected = PebbleList([1, 2])
        assert result == expected

    def test_digits_five_digits(self):
        """digits(12345) should return (1 2 3 4 5)."""
        result = eval_in_env("(digits 12345)")
        expected = PebbleList([1, 2, 3, 4, 5])
        assert result == expected

    def test_digits_with_internal_zeros(self):
        """digits(100) should return (1 0 0)."""
        result = eval_in_env("(digits 100)")
        expected = PebbleList([1, 0, 0])
        assert result == expected

    def test_digits_many_zeros(self):
        """digits(1000000) should return (1 0 0 0 0 0 0)."""
        result = eval_in_env("(digits 1000000)")
        expected = PebbleList([1, 0, 0, 0, 0, 0, 0])
        assert result == expected

    def test_digits_non_integer(self):
        """digits on non-integer should raise EvalError."""
        with pytest.raises(EvalError):
            eval_in_env("(digits 3.14)")

    def test_digits_negative(self):
        """digits on negative number should raise EvalError."""
        with pytest.raises(EvalError):
            eval_in_env("(digits -5)")

    def test_digits_negative_large(self):
        """digits on negative number should raise EvalError."""
        with pytest.raises(EvalError):
            eval_in_env("(digits -12345)")


class TestDigitSum:
    """Test digit-sum function."""

    def test_digit_sum_zero(self):
        """digit-sum(0) should return 0."""
        result = eval_in_env("(digit-sum 0)")
        assert result == 0

    def test_digit_sum_single_digit(self):
        """digit-sum(7) should return 7."""
        result = eval_in_env("(digit-sum 7)")
        assert result == 7

    def test_digit_sum_two_digits(self):
        """digit-sum(12) should return 3."""
        result = eval_in_env("(digit-sum 12)")
        assert result == 3

    def test_digit_sum_five_digits(self):
        """digit-sum(12345) should return 15 (1+2+3+4+5)."""
        result = eval_in_env("(digit-sum 12345)")
        assert result == 15

    def test_digit_sum_ninety_nine(self):
        """digit-sum(99) should return 18 (9+9)."""
        result = eval_in_env("(digit-sum 99)")
        assert result == 18

    def test_digit_sum_with_zeros(self):
        """digit-sum(100) should return 1 (1+0+0)."""
        result = eval_in_env("(digit-sum 100)")
        assert result == 1

    def test_digit_sum_non_integer(self):
        """digit-sum on non-integer should raise EvalError."""
        with pytest.raises(EvalError):
            eval_in_env("(digit-sum 3.14)")

    def test_digit_sum_negative(self):
        """digit-sum on negative number should raise EvalError."""
        with pytest.raises(EvalError):
            eval_in_env("(digit-sum -1)")

    def test_digit_sum_negative_large(self):
        """digit-sum on negative number should raise EvalError."""
        with pytest.raises(EvalError):
            eval_in_env("(digit-sum -12345)")


class TestDigitalRoot:
    """Test digital-root function."""

    def test_digital_root_zero(self):
        """digital-root(0) should return 0."""
        result = eval_in_env("(digital-root 0)")
        assert result == 0

    def test_digital_root_single_digit(self):
        """digital-root(6) should return 6."""
        result = eval_in_env("(digital-root 6)")
        assert result == 6

    def test_digital_root_nine(self):
        """digital-root(9) should return 9."""
        result = eval_in_env("(digital-root 9)")
        assert result == 9

    def test_digital_root_12345(self):
        """digital-root(12345) should return 6.

        12345 -> 1+2+3+4+5=15 -> 1+5=6
        """
        result = eval_in_env("(digital-root 12345)")
        assert result == 6

    def test_digital_root_99(self):
        """digital-root(99) should return 9.

        99 -> 9+9=18 -> 1+8=9
        """
        result = eval_in_env("(digital-root 99)")
        assert result == 9

    def test_digital_root_9875(self):
        """digital-root(9875) should return 2.

        9875 -> 9+8+7+5=29 -> 2+9=11 -> 1+1=2
        """
        result = eval_in_env("(digital-root 9875)")
        assert result == 2

    def test_digital_root_100(self):
        """digital-root(100) should return 1.

        100 -> 1+0+0=1
        """
        result = eval_in_env("(digital-root 100)")
        assert result == 1

    def test_digital_root_19(self):
        """digital-root(19) should return 1.

        19 -> 1+9=10 -> 1+0=1
        """
        result = eval_in_env("(digital-root 19)")
        assert result == 1

    def test_digital_root_non_integer(self):
        """digital-root on non-integer should raise EvalError."""
        with pytest.raises(EvalError):
            eval_in_env("(digital-root 3.14)")

    def test_digital_root_negative(self):
        """digital-root on negative number should raise EvalError."""
        with pytest.raises(EvalError):
            eval_in_env("(digital-root -3)")

    def test_digital_root_negative_large(self):
        """digital-root on negative number should raise EvalError."""
        with pytest.raises(EvalError):
            eval_in_env("(digital-root -12345)")


class TestIntegration:
    """Integration tests combining digits, digit-sum, and digital-root."""

    def test_digit_sum_via_digits(self):
        """digit-sum should equal (sum (digits n))."""
        result1 = eval_in_env("(digit-sum 12345)")
        result2 = eval_in_env("(sum (digits 12345))")
        assert result1 == result2

    def test_digital_root_chain(self):
        """Verify the multi-step digital root for 9875."""
        # 9875 -> digit-sum = 29
        step1 = eval_in_env("(digit-sum 9875)")
        assert step1 == 29

        # 29 -> digit-sum = 11
        step2 = eval_in_env("(digit-sum 29)")
        assert step2 == 11

        # 11 -> digit-sum = 2
        step3 = eval_in_env("(digit-sum 11)")
        assert step3 == 2

        # digital-root(9875) should be 2
        result = eval_in_env("(digital-root 9875)")
        assert result == 2
