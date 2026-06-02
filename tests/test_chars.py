"""Tests for character classification and conversion builtins."""
import pytest
from pebble.evaluator import make_global_env, seval, EvalError
from pebble.reader import read_one
from pebble.types import PebbleList


def eval_str(source):
    """Helper: evaluate a Pebble source string in a fresh global env."""
    env = make_global_env()
    return seval(read_one(source), env)


class TestCharNumeric:
    """Tests for char-numeric? predicate."""

    def test_char_numeric_true(self):
        result = eval_str('(char-numeric? "5")')
        assert result is True

    def test_char_numeric_false_letter(self):
        result = eval_str('(char-numeric? "a")')
        assert result is False

    def test_char_numeric_false_space(self):
        result = eval_str('(char-numeric? " ")')
        assert result is False

    def test_char_numeric_non_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-numeric? 5)')

    def test_char_numeric_empty_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-numeric? "")')

    def test_char_numeric_multi_char_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-numeric? "ab")')


class TestCharAlpha:
    """Tests for char-alpha? predicate."""

    def test_char_alpha_true_lowercase(self):
        result = eval_str('(char-alpha? "a")')
        assert result is True

    def test_char_alpha_true_uppercase(self):
        result = eval_str('(char-alpha? "Z")')
        assert result is True

    def test_char_alpha_false_digit(self):
        result = eval_str('(char-alpha? "5")')
        assert result is False

    def test_char_alpha_false_space(self):
        result = eval_str('(char-alpha? " ")')
        assert result is False

    def test_char_alpha_non_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-alpha? 5)')

    def test_char_alpha_empty_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-alpha? "")')

    def test_char_alpha_multi_char_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-alpha? "ab")')


class TestCharWhitespace:
    """Tests for char-whitespace? predicate."""

    def test_char_whitespace_space(self):
        result = eval_str('(char-whitespace? " ")')
        assert result is True

    def test_char_whitespace_tab(self):
        # Test with actual tab character - test the builtin directly
        env = make_global_env()
        import pebble.builtins
        result = pebble.builtins.builtin_table(lambda f, args: None)['char-whitespace?']('\t')
        assert result is True

    def test_char_whitespace_newline(self):
        # Test with actual newline character - test the builtin directly
        env = make_global_env()
        import pebble.builtins
        result = pebble.builtins.builtin_table(lambda f, args: None)['char-whitespace?']('\n')
        assert result is True

    def test_char_whitespace_false_letter(self):
        result = eval_str('(char-whitespace? "a")')
        assert result is False

    def test_char_whitespace_non_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-whitespace? 5)')

    def test_char_whitespace_empty_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-whitespace? "")')

    def test_char_whitespace_multi_char_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-whitespace? "  ")')


class TestCharUpcase:
    """Tests for char-upcase function."""

    def test_char_upcase_lowercase(self):
        result = eval_str('(char-upcase "a")')
        assert result == "A"

    def test_char_upcase_already_uppercase(self):
        result = eval_str('(char-upcase "A")')
        assert result == "A"

    def test_char_upcase_digit(self):
        result = eval_str('(char-upcase "5")')
        assert result == "5"

    def test_char_upcase_space(self):
        result = eval_str('(char-upcase " ")')
        assert result == " "

    def test_char_upcase_non_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-upcase 5)')

    def test_char_upcase_empty_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-upcase "")')

    def test_char_upcase_multi_char_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-upcase "ab")')


class TestCharDowncase:
    """Tests for char-downcase function."""

    def test_char_downcase_uppercase(self):
        result = eval_str('(char-downcase "A")')
        assert result == "a"

    def test_char_downcase_already_lowercase(self):
        result = eval_str('(char-downcase "a")')
        assert result == "a"

    def test_char_downcase_digit(self):
        result = eval_str('(char-downcase "5")')
        assert result == "5"

    def test_char_downcase_space(self):
        result = eval_str('(char-downcase " ")')
        assert result == " "

    def test_char_downcase_non_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-downcase 5)')

    def test_char_downcase_empty_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-downcase "")')

    def test_char_downcase_multi_char_string(self):
        with pytest.raises(EvalError):
            eval_str('(char-downcase "ab")')


class TestCharToInteger:
    """Tests for char->integer function."""

    def test_char_to_integer_uppercase_a(self):
        result = eval_str('(char->integer "A")')
        assert result == 65

    def test_char_to_integer_lowercase_a(self):
        result = eval_str('(char->integer "a")')
        assert result == 97

    def test_char_to_integer_digit_zero(self):
        result = eval_str('(char->integer "0")')
        assert result == 48

    def test_char_to_integer_space(self):
        result = eval_str('(char->integer " ")')
        assert result == 32

    def test_char_to_integer_non_string(self):
        with pytest.raises(EvalError):
            eval_str('(char->integer 65)')

    def test_char_to_integer_empty_string(self):
        with pytest.raises(EvalError):
            eval_str('(char->integer "")')

    def test_char_to_integer_multi_char_string(self):
        with pytest.raises(EvalError):
            eval_str('(char->integer "ab")')


class TestIntegerToChar:
    """Tests for integer->char function."""

    def test_integer_to_char_65(self):
        result = eval_str('(integer->char 65)')
        assert result == "A"

    def test_integer_to_char_97(self):
        result = eval_str('(integer->char 97)')
        assert result == "a"

    def test_integer_to_char_48(self):
        result = eval_str('(integer->char 48)')
        assert result == "0"

    def test_integer_to_char_32(self):
        result = eval_str('(integer->char 32)')
        assert result == " "

    def test_integer_to_char_non_integer(self):
        with pytest.raises(EvalError):
            eval_str('(integer->char 65.5)')

    def test_integer_to_char_boolean(self):
        with pytest.raises(EvalError):
            eval_str('(integer->char #t)')

    def test_integer_to_char_negative(self):
        with pytest.raises(EvalError):
            eval_str('(integer->char -1)')

    def test_integer_to_char_out_of_range_too_large(self):
        with pytest.raises(EvalError):
            eval_str('(integer->char 9999999)')

    def test_integer_to_char_non_numeric(self):
        with pytest.raises(EvalError):
            eval_str('(integer->char "A")')


class TestCharRoundTrip:
    """Tests for round-trip conversion between char and integer."""

    def test_round_trip_uppercase_z(self):
        result = eval_str('(integer->char (char->integer "Z"))')
        assert result == "Z"

    def test_round_trip_lowercase_z(self):
        result = eval_str('(integer->char (char->integer "z"))')
        assert result == "z"

    def test_round_trip_digit_9(self):
        result = eval_str('(integer->char (char->integer "9"))')
        assert result == "9"

    def test_round_trip_space(self):
        result = eval_str('(integer->char (char->integer " "))')
        assert result == " "


class TestCharIntegration:
    """Integration tests combining character operations with string operations."""

    def test_char_numeric_with_char_at(self):
        result = eval_str('(char-numeric? (char-at "h3llo" 1))')
        assert result is True

    def test_char_alpha_with_char_at(self):
        result = eval_str('(char-alpha? (char-at "h3llo" 0))')
        assert result is True

    def test_char_upcase_with_char_at(self):
        result = eval_str('(char-upcase (char-at "hello" 0))')
        assert result == "H"

    def test_char_downcase_with_char_at(self):
        result = eval_str('(char-downcase (char-at "HELLO" 0))')
        assert result == "h"

    def test_chars_with_string_to_list(self):
        result = eval_str('(map char-numeric? (string->list "a1b2"))')
        # string->list returns list of chars: ("a" "1" "b" "2")
        # map char-numeric? over them: (False True False True)
        assert isinstance(result, PebbleList)
        assert list(result) == [False, True, False, True]

    def test_filter_by_char_alpha(self):
        result = eval_str('(list->string (filter char-alpha? (string->list "a1b2c3")))')
        assert result == "abc"

    def test_filter_by_char_numeric(self):
        result = eval_str('(list->string (filter char-numeric? (string->list "a1b2c3")))')
        assert result == "123"

    def test_map_char_upcase(self):
        result = eval_str('(list->string (map char-upcase (string->list "hello")))')
        assert result == "HELLO"

    def test_map_char_downcase(self):
        result = eval_str('(list->string (map char-downcase (string->list "WORLD")))')
        assert result == "world"
