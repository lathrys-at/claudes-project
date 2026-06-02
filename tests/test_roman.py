"""Tests for Roman numeral conversion functions."""
import pytest
from pebble.evaluator import make_global_env, eval_source, EvalError


def eval_in_env(source):
    """Evaluate a Pebble expression and return the result."""
    env = make_global_env()
    return eval_source(source, env)


class TestIntToRoman:
    """Test int->roman conversion"""

    def test_int_to_roman_1(self):
        result = eval_in_env("(int->roman 1)")
        assert result == "I"

    def test_int_to_roman_4(self):
        result = eval_in_env("(int->roman 4)")
        assert result == "IV"

    def test_int_to_roman_9(self):
        result = eval_in_env("(int->roman 9)")
        assert result == "IX"

    def test_int_to_roman_14(self):
        result = eval_in_env("(int->roman 14)")
        assert result == "XIV"

    def test_int_to_roman_40(self):
        result = eval_in_env("(int->roman 40)")
        assert result == "XL"

    def test_int_to_roman_90(self):
        result = eval_in_env("(int->roman 90)")
        assert result == "XC"

    def test_int_to_roman_400(self):
        result = eval_in_env("(int->roman 400)")
        assert result == "CD"

    def test_int_to_roman_944(self):
        result = eval_in_env("(int->roman 944)")
        assert result == "CMXLIV"

    def test_int_to_roman_2024(self):
        result = eval_in_env("(int->roman 2024)")
        assert result == "MMXXIV"

    def test_int_to_roman_3999(self):
        result = eval_in_env("(int->roman 3999)")
        assert result == "MMMCMXCIX"

    def test_int_to_roman_58(self):
        result = eval_in_env("(int->roman 58)")
        assert result == "LVIII"

    def test_int_to_roman_zero_error(self):
        with pytest.raises(EvalError):
            eval_in_env("(int->roman 0)")

    def test_int_to_roman_4000_error(self):
        with pytest.raises(EvalError):
            eval_in_env("(int->roman 4000)")

    def test_int_to_roman_negative_error(self):
        with pytest.raises(EvalError):
            eval_in_env("(int->roman -5)")


class TestRomanToInt:
    """Test roman->int conversion"""

    def test_roman_to_int_i(self):
        result = eval_in_env('(roman->int "I")')
        assert result == 1

    def test_roman_to_int_iv(self):
        result = eval_in_env('(roman->int "IV")')
        assert result == 4

    def test_roman_to_int_xiv(self):
        result = eval_in_env('(roman->int "XIV")')
        assert result == 14

    def test_roman_to_int_lviii(self):
        result = eval_in_env('(roman->int "LVIII")')
        assert result == 58

    def test_roman_to_int_cmxliv(self):
        result = eval_in_env('(roman->int "CMXLIV")')
        assert result == 944

    def test_roman_to_int_mmxxiv(self):
        result = eval_in_env('(roman->int "MMXXIV")')
        assert result == 2024

    def test_roman_to_int_mmmcmxcix(self):
        result = eval_in_env('(roman->int "MMMCMXCIX")')
        assert result == 3999


class TestRoundTrips:
    """Test that roman->int(int->roman(n)) == n"""

    def test_round_trip_1(self):
        result = eval_in_env("(roman->int (int->roman 1))")
        assert result == 1

    def test_round_trip_4(self):
        result = eval_in_env("(roman->int (int->roman 4))")
        assert result == 4

    def test_round_trip_9(self):
        result = eval_in_env("(roman->int (int->roman 9))")
        assert result == 9

    def test_round_trip_14(self):
        result = eval_in_env("(roman->int (int->roman 14))")
        assert result == 14

    def test_round_trip_40(self):
        result = eval_in_env("(roman->int (int->roman 40))")
        assert result == 40

    def test_round_trip_58(self):
        result = eval_in_env("(roman->int (int->roman 58))")
        assert result == 58

    def test_round_trip_90(self):
        result = eval_in_env("(roman->int (int->roman 90))")
        assert result == 90

    def test_round_trip_400(self):
        result = eval_in_env("(roman->int (int->roman 400))")
        assert result == 400

    def test_round_trip_944(self):
        result = eval_in_env("(roman->int (int->roman 944))")
        assert result == 944

    def test_round_trip_2024(self):
        result = eval_in_env("(roman->int (int->roman 2024))")
        assert result == 2024

    def test_round_trip_3999(self):
        result = eval_in_env("(roman->int (int->roman 3999))")
        assert result == 3999
