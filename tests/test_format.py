"""Tests for the format builtin."""
import pytest
from pebble.evaluator import make_global_env, seval, EvalError
from pebble.reader import read_one


class TestFormatBasic:
    """Tests for basic format functionality."""

    def test_format_no_directives(self):
        """format with no directives returns the template as-is."""
        expr = read_one('(format "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hello"

    def test_format_display_directive_with_number(self):
        """~a outputs argument in display form."""
        expr = read_one('(format "~a + ~a = ~a" 1 2 3)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "1 + 2 = 3"

    def test_format_display_string_no_quotes(self):
        """~a on a string outputs it without quotes (display form)."""
        expr = read_one('(format "~a" "hi")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "hi"

    def test_format_write_string_with_quotes(self):
        """~s on a string outputs it with quotes (write form)."""
        expr = read_one('(format "~s" "hi")')
        env = make_global_env()
        result = seval(expr, env)
        # Should be the 4-character string: " h i "
        assert result == '"hi"'
        assert len(result) == 4

    def test_format_display_list(self):
        """~a on a list outputs it in Lisp form."""
        expr = read_one('(format "~a" (list 1 2 3))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "(1 2 3)"

    def test_format_display_symbol(self):
        """~a on a symbol outputs its name."""
        expr = read_one("(format \"~a\" (quote foo))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == "foo"

    def test_format_newline_directive(self):
        """~% outputs a newline character."""
        expr = read_one('(format "a~%b")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "a\nb"
        assert len(result) == 3  # a, newline, b

    def test_format_tilde_escape(self):
        """~~ outputs a single literal ~."""
        expr = read_one('(format "100~~")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "100~"

    def test_format_mixed_directives(self):
        """format with mixed ~a, ~s, ~%, ~~ directives."""
        expr = read_one('(format "name: ~a, value: ~s~%" "test" 42)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == 'name: test, value: 42\n'

    def test_format_multiple_newlines(self):
        """Multiple ~% directives produce multiple newlines."""
        expr = read_one('(format "a~%~%b")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "a\n\nb"


class TestFormatErrors:
    """Tests for format error handling."""

    def test_format_template_not_string(self):
        """format raises EvalError if template is not a string."""
        expr = read_one('(format 5)')
        env = make_global_env()
        with pytest.raises(EvalError, match="template must be a string"):
            seval(expr, env)

    def test_format_too_few_arguments(self):
        """format raises EvalError if there are too few arguments for directives."""
        expr = read_one('(format "~a ~a" 1)')
        env = make_global_env()
        with pytest.raises(EvalError, match="not enough arguments"):
            seval(expr, env)

    def test_format_too_many_arguments(self):
        """format raises EvalError if there are too many arguments for directives."""
        expr = read_one('(format "~a" 1 2)')
        env = make_global_env()
        with pytest.raises(EvalError, match="too many arguments"):
            seval(expr, env)

    def test_format_unknown_directive(self):
        """format raises EvalError for unknown directives."""
        expr = read_one('(format "~q" 1)')
        env = make_global_env()
        with pytest.raises(EvalError, match="unknown directive"):
            seval(expr, env)

    def test_format_trailing_tilde(self):
        """format raises EvalError if template ends with lone ~."""
        expr = read_one('(format "abc~")')
        env = make_global_env()
        with pytest.raises(EvalError, match="ends with lone"):
            seval(expr, env)

    def test_format_unknown_directive_d(self):
        """~d is an unknown directive."""
        expr = read_one('(format "~d" 42)')
        env = make_global_env()
        with pytest.raises(EvalError, match="unknown directive"):
            seval(expr, env)

    def test_format_unknown_directive_space(self):
        """~ followed by space is an unknown directive."""
        expr = read_one('(format "~ ")')
        env = make_global_env()
        with pytest.raises(EvalError, match="unknown directive"):
            seval(expr, env)


class TestFormatComplexValues:
    """Tests for format with complex values."""

    def test_format_write_string_with_special_chars(self):
        """~s on a string with special characters outputs escaped form."""
        expr = read_one('(format "~s" "hi\\"there")')
        env = make_global_env()
        result = seval(expr, env)
        # Should escape the internal quote
        assert '"' in result
        assert result.startswith('"')
        assert result.endswith('"')

    def test_format_write_list(self):
        """~s on a list outputs it with proper escaping."""
        expr = read_one('(format "~s" (list 1 2 3))')
        env = make_global_env()
        result = seval(expr, env)
        # ~s uses pebble_repr, so list should be represented with parens
        assert result == "(1 2 3)"

    def test_format_display_boolean_true(self):
        """~a on true displays 'true'."""
        expr = read_one('(format "~a" true)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "true"

    def test_format_display_boolean_false(self):
        """~a on false displays 'false'."""
        expr = read_one('(format "~a" false)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "false"

    def test_format_display_float(self):
        """~a on a float displays it as a number string."""
        expr = read_one('(format "~a" 3.14)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "3.14"

    def test_format_write_float(self):
        """~s on a float displays it as a number string."""
        expr = read_one('(format "~s" 3.14)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "3.14"

    def test_format_empty_list(self):
        """~a on an empty list outputs 'nil'."""
        expr = read_one('(format "~a" (list))')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "nil"


class TestFormatEdgeCases:
    """Tests for edge cases and specific behaviors."""

    def test_format_consecutive_directives(self):
        """Consecutive directives without separator."""
        expr = read_one('(format "~a~a" 1 2)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "12"

    def test_format_directive_at_start(self):
        """Directive at the start of template."""
        expr = read_one('(format "~aend" "start")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "startend"

    def test_format_directive_at_end(self):
        """Directive at the end of template."""
        expr = read_one('(format "start~a" "end")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "startend"

    def test_format_many_directives(self):
        """Many directives in a single template."""
        expr = read_one('(format "~a-~a-~a-~a-~a" 1 2 3 4 5)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "1-2-3-4-5"

    def test_format_empty_string_argument(self):
        """Empty string argument is handled correctly."""
        expr = read_one('(format "before~aafter" "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "beforeafter"

    def test_format_zero_argument(self):
        """Zero is displayed/written correctly."""
        expr = read_one('(format "~a" 0)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "0"

    def test_format_negative_number(self):
        """Negative numbers are displayed/written correctly."""
        expr = read_one('(format "~a" -42)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == "-42"

    def test_format_mix_display_write_forms(self):
        """Using both ~a and ~s in the same format string."""
        expr = read_one('(format "display: ~a, write: ~s" "hello" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result == 'display: hello, write: "hello"'
