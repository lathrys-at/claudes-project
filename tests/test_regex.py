"""Tests for the regex engine example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


@pytest.fixture(scope="module")
def regex_env_and_output():
    """Load the regex.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "regex.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestRegex:
    """Tests for the regular expression engine."""

    def test_example_output(self, regex_env_and_output):
        """Test that the example file produces the correct demo output."""
        env, demo_output = regex_env_and_output

        expected_lines = [
            "cat",
            "cat",
            "abbbc",
            "false",
            "cat",
            "123"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_literal_match_found(self, regex_env_and_output):
        """Test literal string match: 'cat' found in 'the cat sat'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "cat" "the cat sat")', env)
        assert result == "cat"

    def test_literal_match_not_found(self, regex_env_and_output):
        """Test literal string not found returns false."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "dog" "the cat sat")', env)
        assert result is False

    def test_wildcard_matches_any_char(self, regex_env_and_output):
        """Test . wildcard matches any single character."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "c.t" "cat")', env)
        assert result == "cat"

    def test_wildcard_different_char(self, regex_env_and_output):
        """Test . wildcard matches 'cut'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "c.t" "cut")', env)
        assert result == "cut"

    def test_wildcard_not_match(self, regex_env_and_output):
        """Test . wildcard does not match when pattern requires different structure."""
        env, _ = regex_env_and_output
        # Pattern "c.t" requires 3 chars, so it should not match "at" (2 chars)
        result = eval_source('(regex-match "c.t" "at")', env)
        assert result is False

    def test_star_zero_matches(self, regex_env_and_output):
        """Test * quantifier with zero matches: 'ab*c' matches 'ac'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "ab*c" "ac")', env)
        assert result == "ac"

    def test_star_one_match(self, regex_env_and_output):
        """Test * quantifier with one match: 'ab*c' matches 'abc'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "ab*c" "abc")', env)
        assert result == "abc"

    def test_star_multiple_matches(self, regex_env_and_output):
        """Test * quantifier with multiple matches: 'ab*c' matches 'abbbc'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "ab*c" "abbbc")', env)
        assert result == "abbbc"

    def test_star_greedy_behavior(self, regex_env_and_output):
        """Test * is greedy: 'a.*b' matches the longest possible substring."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "a.*b" "axxbxxb")', env)
        assert result == "axxbxxb"

    def test_plus_requires_at_least_one(self, regex_env_and_output):
        """Test + quantifier requires at least one: 'ab+c' does not match 'ac'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "ab+c" "ac")', env)
        assert result is False

    def test_plus_one_match(self, regex_env_and_output):
        """Test + with one match: 'ab+c' matches 'abc'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "ab+c" "abc")', env)
        assert result == "abc"

    def test_plus_multiple_matches(self, regex_env_and_output):
        """Test + with multiple matches: 'ab+c' matches 'abbc'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "ab+c" "abbc")', env)
        assert result == "abbc"

    def test_question_zero_matches(self, regex_env_and_output):
        """Test ? quantifier with zero matches: 'colou?r' matches 'color'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "colou?r" "color")', env)
        assert result == "color"

    def test_question_one_match(self, regex_env_and_output):
        """Test ? quantifier with one match: 'colou?r' matches 'colour'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "colou?r" "colour")', env)
        assert result == "colour"

    def test_start_anchor_matches(self, regex_env_and_output):
        """Test ^ anchor: '^cat' matches 'cat dog'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "^cat" "cat dog")', env)
        assert result == "cat"

    def test_start_anchor_no_match(self, regex_env_and_output):
        """Test ^ anchor: '^cat' does not match 'a cat'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "^cat" "a cat")', env)
        assert result is False

    def test_end_anchor_matches(self, regex_env_and_output):
        """Test $ anchor: 'dog$' matches 'the dog'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "dog$" "the dog")', env)
        assert result == "dog"

    def test_end_anchor_no_match(self, regex_env_and_output):
        """Test $ anchor: 'dog$' does not match 'dogs'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "dog$" "dogs")', env)
        assert result is False

    def test_both_anchors_match(self, regex_env_and_output):
        """Test both anchors: '^abc$' matches exactly 'abc'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "^abc$" "abc")', env)
        assert result == "abc"

    def test_both_anchors_no_match_extra_end(self, regex_env_and_output):
        """Test both anchors: '^abc$' does not match 'abcd'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "^abc$" "abcd")', env)
        assert result is False

    def test_both_anchors_no_match_extra_start(self, regex_env_and_output):
        """Test both anchors: '^abc$' does not match 'xabc'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "^abc$" "xabc")', env)
        assert result is False

    def test_char_class_range_digits(self, regex_env_and_output):
        """Test character class with range: '[0-9]+' extracts '123' from 'abc123def'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "[0-9]+" "abc123def")', env)
        assert result == "123"

    def test_char_class_range_lowercase(self, regex_env_and_output):
        """Test character class with range: '[a-z]+' returns 'abc'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "[a-z]+" "ABC123abc")', env)
        assert result == "abc"

    def test_negated_class_matches(self, regex_env_and_output):
        """Test negated class: '[^0-9]' matches 'a' in '5a'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "[^0-9]" "5a")', env)
        assert result == "a"

    def test_negated_class_no_match(self, regex_env_and_output):
        """Test negated class: '[^0-9]+' does not match when all chars are digits."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "[^0-9]+" "12345")', env)
        assert result is False

    def test_escaped_literal_dot(self, regex_env_and_output):
        """Test escaped dot: '\\.' matches literal '.' in '3.14'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "\\\\." "3.14")', env)
        assert result == "."

    def test_unescaped_dot(self, regex_env_and_output):
        """Test unescaped dot: '.' matches any character like 'x'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "." "x")', env)
        assert result == "x"

    def test_escaped_star(self, regex_env_and_output):
        """Test escaped star: '\\*' matches literal '*'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "\\\\*" "a*b")', env)
        assert result == "*"

    def test_empty_pattern(self, regex_env_and_output):
        """Test empty pattern matches empty string."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "" "")', env)
        assert result == ""

    def test_empty_pattern_matches_start(self, regex_env_and_output):
        """Test empty pattern matches at start of any string."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "" "abc")', env)
        assert result == ""

    def test_complex_pattern_match(self, regex_env_and_output):
        """Test complex pattern: '^[a-z]+[0-9]+$' matches 'abc123'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "^[a-z]+[0-9]+$" "abc123")', env)
        assert result == "abc123"

    def test_complex_pattern_no_match_extra_chars(self, regex_env_and_output):
        """Test complex pattern: '^[a-z]+[0-9]+$' rejects 'abc123x'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "^[a-z]+[0-9]+$" "abc123x")', env)
        assert result is False

    def test_complex_pattern_no_match_wrong_order(self, regex_env_and_output):
        """Test complex pattern: '^[a-z]+[0-9]+$' rejects '1abc'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "^[a-z]+[0-9]+$" "1abc")', env)
        assert result is False

    def test_regex_match_question(self, regex_env_and_output):
        """Test regex-match? returns true for matching pattern."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match? "cat" "the cat sat")', env)
        assert result is True

    def test_regex_match_question_false(self, regex_env_and_output):
        """Test regex-match? returns false for non-matching pattern."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match? "dog" "the cat sat")', env)
        assert result is False

    def test_unanchored_match_middle(self, regex_env_and_output):
        """Test unanchored match finds pattern anywhere in text."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "cat" "the cat is here")', env)
        assert result == "cat"

    def test_unanchored_match_earliest(self, regex_env_and_output):
        """Test unanchored match returns leftmost match."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "a" "banana")', env)
        assert result == "a"

    def test_char_class_single_char(self, regex_env_and_output):
        """Test character class with single char: '[abc]' matches 'b'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "[abc]" "b")', env)
        assert result == "b"

    def test_char_class_multiple_ranges(self, regex_env_and_output):
        """Test character class with multiple ranges: '[a-zA-Z0-9]' matches 'X'."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "[a-zA-Z]" "X")', env)
        assert result == "X"

    def test_wildcard_dot_in_class(self, regex_env_and_output):
        """Test that . inside class is literal (not wildcard)."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "[.]" ".")', env)
        assert result == "."

    def test_star_with_wildcard(self, regex_env_and_output):
        """Test .*: match zero or more of any character."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "a.*z" "axxxz")', env)
        assert result == "axxxz"

    def test_multiple_literals(self, regex_env_and_output):
        """Test matching multiple literal characters."""
        env, _ = regex_env_and_output
        result = eval_source('(regex-match "hello" "hello world")', env)
        assert result == "hello"
