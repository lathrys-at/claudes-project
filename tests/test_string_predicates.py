"""Tests for string predicate functions: palindrome? and anagram?."""
import pytest
from pebble.evaluator import make_global_env, eval_source, EvalError


def eval_in_env(source):
    """Evaluate a Pebble expression and return the result."""
    env = make_global_env()
    return eval_source(source, env)


class TestPalindrome:
    """Test palindrome? function."""

    def test_palindrome_racecar(self):
        """'racecar' is a palindrome."""
        result = eval_in_env("(palindrome? \"racecar\")")
        assert result is True

    def test_palindrome_abba(self):
        """'abba' is a palindrome."""
        result = eval_in_env("(palindrome? \"abba\")")
        assert result is True

    def test_palindrome_single_char(self):
        """Single character is a palindrome."""
        result = eval_in_env("(palindrome? \"a\")")
        assert result is True

    def test_palindrome_empty_string(self):
        """Empty string is a palindrome."""
        result = eval_in_env("(palindrome? \"\")")
        assert result is True

    def test_not_palindrome_hello(self):
        """'hello' is not a palindrome."""
        result = eval_in_env("(palindrome? \"hello\")")
        assert result is False

    def test_not_palindrome_abca(self):
        """'abca' is not a palindrome."""
        result = eval_in_env("(palindrome? \"abca\")")
        assert result is False

    def test_palindrome_case_sensitive_abba(self):
        """'Abba' is not a palindrome (case-sensitive)."""
        result = eval_in_env("(palindrome? \"Abba\")")
        assert result is False


class TestAnagram:
    """Test anagram? function."""

    def test_anagram_listen_silent(self):
        """'listen' and 'silent' are anagrams."""
        result = eval_in_env("(anagram? \"listen\" \"silent\")")
        assert result is True

    def test_anagram_aabb_bbaa(self):
        """'aabb' and 'bbaa' are anagrams."""
        result = eval_in_env("(anagram? \"aabb\" \"bbaa\")")
        assert result is True

    def test_anagram_empty_strings(self):
        """Empty strings are anagrams of each other."""
        result = eval_in_env("(anagram? \"\" \"\")")
        assert result is True

    def test_anagram_abc_cba(self):
        """'abc' and 'cba' are anagrams."""
        result = eval_in_env("(anagram? \"abc\" \"cba\")")
        assert result is True

    def test_not_anagram_abc_abd(self):
        """'abc' and 'abd' are not anagrams (different characters)."""
        result = eval_in_env("(anagram? \"abc\" \"abd\")")
        assert result is False

    def test_not_anagram_different_lengths(self):
        """'abc' and 'ab' are not anagrams (different lengths)."""
        result = eval_in_env("(anagram? \"abc\" \"ab\")")
        assert result is False

    def test_not_anagram_different_multiplicities(self):
        """'aab' and 'abb' are not anagrams (different multiplicities)."""
        result = eval_in_env("(anagram? \"aab\" \"abb\")")
        assert result is False

    def test_anagram_case_sensitive(self):
        """'Listen' and 'silent' are not anagrams (case-sensitive: 'L' vs 'l')."""
        result = eval_in_env("(anagram? \"Listen\" \"silent\")")
        assert result is False
