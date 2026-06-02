"""Tests for text utilities: words, unwords, lines, unlines."""
import pytest
from pebble.evaluator import make_global_env, eval_source, EvalError


def eval_in_env(source):
    """Evaluate a Pebble expression and return the result."""
    env = make_global_env()
    return eval_source(source, env)


class TestWords:
    """Test the words function."""

    def test_words_basic(self):
        result = eval_in_env('(words "hello world")')
        assert result == ("hello", "world")

    def test_words_leading_trailing_spaces(self):
        result = eval_in_env('(words "  hello   world  ")')
        assert result == ("hello", "world")

    def test_words_single_word(self):
        result = eval_in_env('(words "one")')
        assert result == ("one",)

    def test_words_empty_string(self):
        result = eval_in_env('(words "")')
        # nil should be falsy and equal to empty PebbleList
        assert len(result) == 0

    def test_words_whitespace_only(self):
        result = eval_in_env('(words "   ")')
        # nil should be falsy and equal to empty PebbleList
        assert len(result) == 0

    def test_words_with_tabs_and_newlines(self):
        result = eval_in_env('(words "a\tb\nc")')
        assert result == ("a", "b", "c")


class TestUnwords:
    """Test the unwords function."""

    def test_unwords_basic(self):
        result = eval_in_env('(unwords (list "a" "b" "c"))')
        assert result == "a b c"

    def test_unwords_single_word(self):
        result = eval_in_env('(unwords (list "hello"))')
        assert result == "hello"

    def test_unwords_empty_list(self):
        result = eval_in_env('(unwords nil)')
        assert result == ""


class TestLines:
    """Test the lines function."""

    def test_lines_basic(self):
        result = eval_in_env('(lines "a\\nb\\nc")')
        assert result == ("a", "b", "c")

    def test_lines_single_line(self):
        result = eval_in_env('(lines "a")')
        assert result == ("a",)

    def test_lines_trailing_newline(self):
        result = eval_in_env('(lines "a\\n")')
        assert result == ("a", "")

    def test_lines_empty_string(self):
        result = eval_in_env('(lines "")')
        assert result == ("",)


class TestUnlines:
    """Test the unlines function."""

    def test_unlines_basic(self):
        result = eval_in_env('(unlines (list "a" "b" "c"))')
        assert result == "a\nb\nc"

    def test_unlines_single_line(self):
        result = eval_in_env('(unlines (list "a"))')
        assert result == "a"

    def test_unlines_empty_list(self):
        result = eval_in_env('(unlines nil)')
        assert result == ""


class TestRoundTrips:
    """Test round-trip conversions."""

    def test_unlines_lines_basic(self):
        result = eval_in_env('(unlines (lines "a\\nb\\nc"))')
        assert result == "a\nb\nc"

    def test_unlines_lines_trailing_newline(self):
        result = eval_in_env('(unlines (lines "a\\n"))')
        assert result == "a\n"

    def test_unwords_words_with_spaces(self):
        result = eval_in_env('(unwords (words "  hello   world  "))')
        assert result == "hello world"
