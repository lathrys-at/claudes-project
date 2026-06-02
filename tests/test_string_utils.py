"""Tests for string utility functions."""
import pytest
from pebble.evaluator import make_global_env, eval_source, EvalError


def eval_in_env(source):
    """Evaluate a Pebble expression and return the result."""
    env = make_global_env()
    return eval_source(source, env)


class TestStringReverse:
    """Test string-reverse function."""

    def test_reverse_abc(self):
        result = eval_in_env('(string-reverse "abc")')
        assert result == "cba"

    def test_reverse_empty_string(self):
        result = eval_in_env('(string-reverse "")')
        assert result == ""

    def test_reverse_racecar(self):
        result = eval_in_env('(string-reverse "racecar")')
        assert result == "racecar"

    def test_reverse_single_char(self):
        result = eval_in_env('(string-reverse "a")')
        assert result == "a"

    def test_reverse_roundtrip(self):
        """Reversing twice should return the original."""
        result = eval_in_env('(string-reverse (string-reverse "hello world"))')
        assert result == "hello world"


class TestCapitalize:
    """Test capitalize function."""

    def test_capitalize_hello(self):
        result = eval_in_env('(capitalize "hello")')
        assert result == "Hello"

    def test_capitalize_empty_string(self):
        result = eval_in_env('(capitalize "")')
        assert result == ""

    def test_capitalize_single_char_a(self):
        result = eval_in_env('(capitalize "a")')
        assert result == "A"

    def test_capitalize_already_capitalized(self):
        result = eval_in_env('(capitalize "Hello")')
        assert result == "Hello"

    def test_capitalize_non_letter_first_char(self):
        """Non-letter first character should remain unchanged."""
        result = eval_in_env('(capitalize "123")')
        assert result == "123"

    def test_capitalize_digit_followed_by_letter(self):
        result = eval_in_env('(capitalize "1abc")')
        assert result == "1abc"

    def test_capitalize_preserves_rest(self):
        """Capitalize should only affect the first character."""
        result = eval_in_env('(capitalize "hELLO")')
        assert result == "HELLO"


class TestStringPadLeft:
    """Test string-pad-left function."""

    def test_pad_left_42_width_5_with_0(self):
        result = eval_in_env('(string-pad-left "42" 5 "0")')
        assert result == "00042"

    def test_pad_left_hello_width_3_with_0(self):
        """String already wider than width should be returned unchanged."""
        result = eval_in_env('(string-pad-left "hello" 3 "0")')
        assert result == "hello"

    def test_pad_left_empty_string(self):
        result = eval_in_env('(string-pad-left "" 3 "x")')
        assert result == "xxx"

    def test_pad_left_exact_width(self):
        """String at exact width should be returned unchanged."""
        result = eval_in_env('(string-pad-left "hi" 2 "0")')
        assert result == "hi"

    def test_pad_left_already_exceeded(self):
        """String wider than width should be returned unchanged."""
        result = eval_in_env('(string-pad-left "abcde" 3 "x")')
        assert result == "abcde"

    def test_pad_left_different_fill_char(self):
        result = eval_in_env('(string-pad-left "test" 7 "*")')
        assert result == "***test"

    def test_pad_left_invalid_fill_empty(self):
        """Fill must be exactly 1 character."""
        with pytest.raises(EvalError):
            eval_in_env('(string-pad-left "test" 5 "")')

    def test_pad_left_invalid_fill_too_long(self):
        """Fill must be exactly 1 character."""
        with pytest.raises(EvalError):
            eval_in_env('(string-pad-left "test" 5 "ab")')


class TestStringPadRight:
    """Test string-pad-right function."""

    def test_pad_right_42_width_5_with_0(self):
        result = eval_in_env('(string-pad-right "42" 5 "0")')
        assert result == "42000"

    def test_pad_right_hello_width_3_with_star(self):
        """String already wider than width should be returned unchanged."""
        result = eval_in_env('(string-pad-right "hello" 3 "*")')
        assert result == "hello"

    def test_pad_right_empty_string(self):
        result = eval_in_env('(string-pad-right "" 3 "x")')
        assert result == "xxx"

    def test_pad_right_exact_width(self):
        """String at exact width should be returned unchanged."""
        result = eval_in_env('(string-pad-right "hi" 2 "0")')
        assert result == "hi"

    def test_pad_right_already_exceeded(self):
        """String wider than width should be returned unchanged."""
        result = eval_in_env('(string-pad-right "abcde" 3 "x")')
        assert result == "abcde"

    def test_pad_right_different_fill_char(self):
        result = eval_in_env('(string-pad-right "test" 7 "*")')
        assert result == "test***"

    def test_pad_right_invalid_fill_empty(self):
        """Fill must be exactly 1 character."""
        with pytest.raises(EvalError):
            eval_in_env('(string-pad-right "test" 5 "")')

    def test_pad_right_invalid_fill_too_long(self):
        """Fill must be exactly 1 character."""
        with pytest.raises(EvalError):
            eval_in_env('(string-pad-right "test" 5 "ab")')
