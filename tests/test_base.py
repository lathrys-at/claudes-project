"""Tests for number base conversion functions."""
import pytest
from pebble.evaluator import make_global_env, eval_source, EvalError


def eval_in_env(source):
    """Evaluate a Pebble expression and return the result."""
    env = make_global_env()
    return eval_source(source, env)


class TestNumberToBinary:
    """Test number->binary function."""

    def test_13_to_binary(self):
        result = eval_in_env("(number->binary 13)")
        assert result == "1101"

    def test_0_to_binary(self):
        result = eval_in_env("(number->binary 0)")
        assert result == "0"

    def test_1_to_binary(self):
        result = eval_in_env("(number->binary 1)")
        assert result == "1"

    def test_255_to_binary(self):
        result = eval_in_env("(number->binary 255)")
        assert result == "11111111"


class TestNumberToHex:
    """Test number->hex function."""

    def test_255_to_hex(self):
        result = eval_in_env("(number->hex 255)")
        assert result == "ff"

    def test_0_to_hex(self):
        result = eval_in_env("(number->hex 0)")
        assert result == "0"

    def test_16_to_hex(self):
        result = eval_in_env("(number->hex 16)")
        assert result == "10"

    def test_4095_to_hex(self):
        result = eval_in_env("(number->hex 4095)")
        assert result == "fff"


class TestNumberToBase:
    """Test number->base function."""

    def test_100_to_base_2(self):
        result = eval_in_env("(number->base 100 2)")
        assert result == "1100100"

    def test_100_to_base_8(self):
        result = eval_in_env("(number->base 100 8)")
        assert result == "144"

    def test_100_to_base_16(self):
        result = eval_in_env("(number->base 100 16)")
        assert result == "64"


class TestBinaryToNumber:
    """Test binary->number function."""

    def test_1101_to_number(self):
        result = eval_in_env("(binary->number \"1101\")")
        assert result == 13

    def test_11111111_to_number(self):
        result = eval_in_env("(binary->number \"11111111\")")
        assert result == 255


class TestBaseToNumber:
    """Test base->number function."""

    def test_1101_binary_to_number(self):
        result = eval_in_env("(base->number \"1101\" 2)")
        assert result == 13

    def test_ff_hex_to_number(self):
        result = eval_in_env("(base->number \"ff\" 16)")
        assert result == 255

    def test_64_hex_to_number(self):
        result = eval_in_env("(base->number \"64\" 16)")
        assert result == 100

    def test_144_octal_to_number(self):
        result = eval_in_env("(base->number \"144\" 8)")
        assert result == 100


class TestHexToNumber:
    """Test hex->number function."""

    def test_ff_to_number(self):
        result = eval_in_env("(hex->number \"ff\")")
        assert result == 255


class TestRoundTrips:
    """Test round-trip conversions."""

    def test_roundtrip_hex_12345(self):
        result = eval_in_env("(base->number (number->base 12345 16) 16)")
        assert result == 12345

    def test_roundtrip_binary_12345(self):
        result = eval_in_env("(binary->number (number->binary 12345))")
        assert result == 12345


class TestErrorCases:
    """Test error cases."""

    def test_negative_number(self):
        with pytest.raises(EvalError):
            eval_in_env("(number->base -5 2)")

    def test_base_too_small(self):
        with pytest.raises(EvalError):
            eval_in_env("(number->base 10 1)")

    def test_base_too_large(self):
        with pytest.raises(EvalError):
            eval_in_env("(number->base 10 17)")

    def test_base_to_number_invalid_base_small(self):
        with pytest.raises(EvalError):
            eval_in_env("(base->number \"12\" 1)")

    def test_base_to_number_invalid_digit(self):
        with pytest.raises(EvalError):
            eval_in_env("(base->number \"1102\" 2)")

    def test_empty_string(self):
        with pytest.raises(EvalError):
            eval_in_env("(base->number \"\" 2)")
