"""Tests for the new string manipulation builtins."""
import pytest
from pebble.evaluator import make_global_env, EvalError, seval
from pebble.reader import read_one
from pebble.types import Symbol, PebbleList, NIL


class TestStringUpcase:
    """Tests for string-upcase builtin."""

    def test_upcase_lowercase(self):
        expr = read_one('(string-upcase "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "HELLO"

    def test_upcase_mixed_case(self):
        expr = read_one('(string-upcase "HeLLo")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "HELLO"

    def test_upcase_already_uppercase(self):
        expr = read_one('(string-upcase "HELLO")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "HELLO"

    def test_upcase_empty_string(self):
        expr = read_one('(string-upcase "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == ""

    def test_upcase_with_numbers_and_symbols(self):
        expr = read_one('(string-upcase "abc123")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "ABC123"

    def test_upcase_non_string_argument_number(self):
        expr = read_one('(string-upcase 42)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-upcase: argument must be a string"):
            seval(expr, env)

    def test_upcase_non_string_argument_symbol(self):
        expr = read_one('(string-upcase (quote foo))')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-upcase: argument must be a string"):
            seval(expr, env)


class TestStringDowncase:
    """Tests for string-downcase builtin."""

    def test_downcase_uppercase(self):
        expr = read_one('(string-downcase "HELLO")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_downcase_mixed_case(self):
        expr = read_one('(string-downcase "HeLLo")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_downcase_already_lowercase(self):
        expr = read_one('(string-downcase "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_downcase_empty_string(self):
        expr = read_one('(string-downcase "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == ""

    def test_downcase_non_string_argument(self):
        expr = read_one('(string-downcase 42)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-downcase: argument must be a string"):
            seval(expr, env)


class TestStringContains:
    """Tests for string-contains? builtin."""

    def test_contains_true(self):
        expr = read_one('(string-contains? "hello world" "world")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_contains_false(self):
        expr = read_one('(string-contains? "abc" "x")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_contains_empty_substring(self):
        expr = read_one('(string-contains? "abc" "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_contains_empty_string_and_empty_substring(self):
        expr = read_one('(string-contains? "" "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_contains_substring_equals_string(self):
        expr = read_one('(string-contains? "hello" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_contains_non_string_first_argument(self):
        expr = read_one('(string-contains? 42 "x")')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-contains\\?.*first argument"):
            seval(expr, env)

    def test_contains_non_string_second_argument(self):
        expr = read_one('(string-contains? "hello" 42)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-contains\\?.*second argument"):
            seval(expr, env)


class TestStringIndex:
    """Tests for string-index builtin."""

    def test_index_found(self):
        expr = read_one('(string-index "hello" "l")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == 2

    def test_index_not_found(self):
        expr = read_one('(string-index "hello" "z")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == -1

    def test_index_empty_substring(self):
        expr = read_one('(string-index "hello" "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == 0

    def test_index_first_occurrence(self):
        expr = read_one('(string-index "hello" "l")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == 2

    def test_index_whole_string(self):
        expr = read_one('(string-index "hello" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == 0

    def test_index_empty_string(self):
        expr = read_one('(string-index "" "x")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == -1

    def test_index_non_string_first_argument(self):
        expr = read_one('(string-index 42 "x")')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-index: first argument must be a string"):
            seval(expr, env)


class TestStringPrefix:
    """Tests for string-prefix? builtin."""

    def test_prefix_true(self):
        expr = read_one('(string-prefix? "he" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_prefix_false(self):
        expr = read_one('(string-prefix? "lo" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_prefix_equal_strings(self):
        expr = read_one('(string-prefix? "hello" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_prefix_empty_prefix(self):
        expr = read_one('(string-prefix? "" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_prefix_longer_than_string(self):
        expr = read_one('(string-prefix? "helloo" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_prefix_non_string_first_argument(self):
        expr = read_one('(string-prefix? 42 "hello")')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-prefix\\?.*first argument"):
            seval(expr, env)


class TestStringSuffix:
    """Tests for string-suffix? builtin."""

    def test_suffix_true(self):
        expr = read_one('(string-suffix? "lo" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_suffix_false(self):
        expr = read_one('(string-suffix? "he" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_suffix_equal_strings(self):
        expr = read_one('(string-suffix? "hello" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_suffix_empty_suffix(self):
        expr = read_one('(string-suffix? "" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_suffix_longer_than_string(self):
        expr = read_one('(string-suffix? "helloo" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_suffix_non_string_first_argument(self):
        expr = read_one('(string-suffix? 42 "hello")')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-suffix\\?.*first argument"):
            seval(expr, env)


class TestStringRepeat:
    """Tests for string-repeat builtin."""

    def test_repeat_positive(self):
        expr = read_one('(string-repeat "ab" 3)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "ababab"

    def test_repeat_zero(self):
        expr = read_one('(string-repeat "x" 0)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == ""

    def test_repeat_one(self):
        expr = read_one('(string-repeat "hello" 1)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_repeat_empty_string(self):
        expr = read_one('(string-repeat "" 5)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == ""

    def test_repeat_negative_count(self):
        expr = read_one('(string-repeat "x" -1)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-repeat: count must be non-negative"):
            seval(expr, env)

    def test_repeat_non_integer_count(self):
        expr = read_one('(string-repeat "x" 2.5)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-repeat: second argument must be an integer"):
            seval(expr, env)

    def test_repeat_boolean_count(self):
        expr = read_one('(string-repeat "x" true)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-repeat.*argument must be an integer"):
            seval(expr, env)

    def test_repeat_non_string_argument(self):
        expr = read_one('(string-repeat 42 3)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-repeat: first argument must be a string"):
            seval(expr, env)


class TestStringReplace:
    """Tests for string-replace builtin."""

    def test_replace_simple(self):
        expr = read_one('(string-replace "a-b-c" "-" "+")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "a+b+c"

    def test_replace_multiple_occurrences(self):
        expr = read_one('(string-replace "hello" "l" "L")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "heLLo"

    def test_replace_not_found(self):
        expr = read_one('(string-replace "hello" "x" "y")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_replace_with_empty_new(self):
        expr = read_one('(string-replace "hello" "l" "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "heo"

    def test_replace_empty_old_raises_error(self):
        expr = read_one('(string-replace "hello" "" "x")')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-replace: old string must be non-empty"):
            seval(expr, env)

    def test_replace_non_string_first_argument(self):
        expr = read_one('(string-replace 42 "x" "y")')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-replace: first argument must be a string"):
            seval(expr, env)

    def test_replace_non_string_second_argument(self):
        expr = read_one('(string-replace "hello" 42 "y")')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-replace: second argument must be a string"):
            seval(expr, env)

    def test_replace_non_string_third_argument(self):
        expr = read_one('(string-replace "hello" "l" 42)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-replace: third argument must be a string"):
            seval(expr, env)


class TestStringTrim:
    """Tests for string-trim builtin."""

    def test_trim_spaces(self):
        expr = read_one('(string-trim "  hi  ")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hi"

    def test_trim_leading_spaces(self):
        expr = read_one('(string-trim "  hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_trim_trailing_spaces(self):
        expr = read_one('(string-trim "hello  ")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_trim_tabs(self):
        expr = read_one('(string-trim "\t\thello\t\t")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_trim_newlines(self):
        expr = read_one('(string-trim "\nhello\n")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_trim_mixed_whitespace(self):
        expr = read_one('(string-trim " \t\nhello\n\t ")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_trim_no_whitespace(self):
        expr = read_one('(string-trim "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_trim_empty_string(self):
        expr = read_one('(string-trim "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == ""

    def test_trim_only_whitespace(self):
        expr = read_one('(string-trim "   ")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == ""

    def test_trim_non_string_argument(self):
        expr = read_one('(string-trim 42)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string-trim: argument must be a string"):
            seval(expr, env)


class TestCharAt:
    """Tests for char-at builtin."""

    def test_char_at_valid_index(self):
        expr = read_one('(char-at "hello" 1)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "e"

    def test_char_at_first_char(self):
        expr = read_one('(char-at "hello" 0)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "h"

    def test_char_at_last_char(self):
        expr = read_one('(char-at "hello" 4)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "o"

    def test_char_at_out_of_range_positive(self):
        expr = read_one('(char-at "hello" 5)')
        env = make_global_env()
        with pytest.raises(EvalError, match="char-at: index 5 out of range"):
            seval(expr, env)

    def test_char_at_negative_index(self):
        expr = read_one('(char-at "hello" -1)')
        env = make_global_env()
        with pytest.raises(EvalError, match="char-at: index -1 out of range"):
            seval(expr, env)

    def test_char_at_non_integer_index(self):
        expr = read_one('(char-at "hello" 1.5)')
        env = make_global_env()
        with pytest.raises(EvalError, match="char-at: second argument must be an integer"):
            seval(expr, env)

    def test_char_at_boolean_index(self):
        expr = read_one('(char-at "hello" true)')
        env = make_global_env()
        with pytest.raises(EvalError, match="char-at.*argument must be an integer"):
            seval(expr, env)

    def test_char_at_non_string_first_argument(self):
        expr = read_one('(char-at 42 0)')
        env = make_global_env()
        with pytest.raises(EvalError, match="char-at: first argument must be a string"):
            seval(expr, env)

    def test_char_at_returns_string(self):
        expr = read_one('(string? (char-at "hello" 0))')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True


class TestStringToList:
    """Tests for string->list builtin."""

    def test_string_to_list_non_empty(self):
        expr = read_one('(string->list "abc")')
        env = make_global_env()
        result = seval(expr, env)
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == "a"
        assert result[1] == "b"
        assert result[2] == "c"

    def test_string_to_list_empty(self):
        expr = read_one('(string->list "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == NIL

    def test_string_to_list_single_char(self):
        expr = read_one('(string->list "x")')
        env = make_global_env()
        result = seval(expr, env)
        assert len(result) == 1
        assert result[0] == "x"

    def test_string_to_list_non_string_argument(self):
        expr = read_one('(string->list 42)')
        env = make_global_env()
        with pytest.raises(EvalError, match="string->list: argument must be a string"):
            seval(expr, env)


class TestListToString:
    """Tests for list->string builtin."""

    def test_list_to_string_non_empty(self):
        expr = read_one('(list->string (list "a" "b" "c"))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "abc"

    def test_list_to_string_empty(self):
        expr = read_one('(list->string (list))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == ""

    def test_list_to_string_single_element(self):
        expr = read_one('(list->string (list "x"))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "x"

    def test_list_to_string_with_non_string_element(self):
        expr = read_one('(list->string (list "a" 42 "c"))')
        env = make_global_env()
        with pytest.raises(EvalError, match="list->string: all elements must be strings"):
            seval(expr, env)

    def test_list_to_string_with_symbol_element(self):
        expr = read_one('(list->string (list "a" (quote foo) "c"))')
        env = make_global_env()
        with pytest.raises(EvalError, match="list->string: all elements must be strings"):
            seval(expr, env)

    def test_list_to_string_non_list_argument(self):
        expr = read_one('(list->string 42)')
        env = make_global_env()
        with pytest.raises(EvalError, match="list->string: argument must be a list"):
            seval(expr, env)


class TestStringListRoundTrip:
    """Tests for string->list and list->string round-trip."""

    def test_roundtrip_hello(self):
        expr = read_one('(list->string (string->list "hello"))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_roundtrip_empty(self):
        expr = read_one('(list->string (string->list ""))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == ""

    def test_roundtrip_special_chars(self):
        expr = read_one('(list->string (string->list "!@#$%"))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "!@#$%"

    def test_roundtrip_whitespace(self):
        expr = read_one('(list->string (string->list " \t\n "))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == " \t\n "


class TestEdgeCases:
    """Edge cases and integration tests."""

    def test_empty_string_cases(self):
        """Test various builtins with empty strings."""
        exprs = [
            ('(string-upcase "")', ""),
            ('(string-downcase "")', ""),
            ('(string-contains? "" "")', True),
            ('(string-index "" "")', 0),
            ('(string-prefix? "" "")', True),
            ('(string-suffix? "" "")', True),
            ('(string-repeat "" 5)', ""),
            ('(string-trim "")', ""),
        ]
        env = make_global_env()
        for expr_str, expected in exprs:
            expr = read_one(expr_str)
            result = seval(expr, env)
            assert result == expected, f"Failed for {expr_str}"

    def test_upcase_downcase_roundtrip(self):
        """Test that upcase and downcase compose properly."""
        expr = read_one('(string-downcase (string-upcase "Hello"))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_repeated_string_operations(self):
        """Test chaining multiple string operations."""
        expr = read_one('(string-replace (string-upcase (string-trim "  hi there  ")) " " "_")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "HI_THERE"
