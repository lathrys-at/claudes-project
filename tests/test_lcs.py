"""Tests for the lcs-length (Longest Common Subsequence) function."""
import pytest
from pebble.evaluator import make_global_env, eval_source


class TestLcsLength:
    """Tests for the lcs-length function in the standard library."""

    def test_classic_example_abcbdab_bdcab(self):
        """Test the classic example: LCS of 'ABCBDAB' and 'BDCAB' should be 4 (e.g., 'BCAB')."""
        env = make_global_env()
        result = eval_source('(lcs-length "ABCBDAB" "BDCAB")', env)
        assert result == 4

    def test_classic_example_aggtab_gxtxayb(self):
        """Test another classic example: LCS of 'AGGTAB' and 'GXTXAYB' should be 4 (e.g., 'GTAB')."""
        env = make_global_env()
        result = eval_source('(lcs-length "AGGTAB" "GXTXAYB")', env)
        assert result == 4

    def test_identical_strings(self):
        """Test LCS of identical strings: (lcs-length 'abc' 'abc') should be 3."""
        env = make_global_env()
        result = eval_source('(lcs-length "abc" "abc")', env)
        assert result == 3

    def test_partial_subsequence(self):
        """Test LCS of 'abcde' and 'ace' should be 3 (the LCS is 'ace')."""
        env = make_global_env()
        result = eval_source('(lcs-length "abcde" "ace")', env)
        assert result == 3

    def test_no_common_subsequence(self):
        """Test LCS with no common characters: (lcs-length 'abc' 'def') should be 0."""
        env = make_global_env()
        result = eval_source('(lcs-length "abc" "def")', env)
        assert result == 0

    def test_empty_first_string(self):
        """Test LCS with empty first string: (lcs-length '' 'abc') should be 0."""
        env = make_global_env()
        result = eval_source('(lcs-length "" "abc")', env)
        assert result == 0

    def test_empty_second_string(self):
        """Test LCS with empty second string: (lcs-length 'abc' '') should be 0."""
        env = make_global_env()
        result = eval_source('(lcs-length "abc" "")', env)
        assert result == 0

    def test_both_empty_strings(self):
        """Test LCS of two empty strings: (lcs-length '' '') should be 0."""
        env = make_global_env()
        result = eval_source('(lcs-length "" "")', env)
        assert result == 0

    def test_single_char_same(self):
        """Test LCS of identical single characters: (lcs-length 'a' 'a') should be 1."""
        env = make_global_env()
        result = eval_source('(lcs-length "a" "a")', env)
        assert result == 1

    def test_single_char_different(self):
        """Test LCS of different single characters: (lcs-length 'a' 'b') should be 0."""
        env = make_global_env()
        result = eval_source('(lcs-length "a" "b")', env)
        assert result == 0

    def test_one_char_subsequence(self):
        """Test LCS with only one character in common: (lcs-length 'AB' 'BA') should be 1."""
        env = make_global_env()
        result = eval_source('(lcs-length "AB" "BA")', env)
        assert result == 1

    def test_symmetry_abcbdab_bdcab(self):
        """Test symmetry: LCS('ABCBDAB', 'BDCAB') == LCS('BDCAB', 'ABCBDAB')."""
        env = make_global_env()
        result1 = eval_source('(lcs-length "ABCBDAB" "BDCAB")', env)
        result2 = eval_source('(lcs-length "BDCAB" "ABCBDAB")', env)
        assert result1 == result2 == 4

    def test_symmetry_aggtab_gxtxayb(self):
        """Test symmetry: LCS('AGGTAB', 'GXTXAYB') == LCS('GXTXAYB', 'AGGTAB')."""
        env = make_global_env()
        result1 = eval_source('(lcs-length "AGGTAB" "GXTXAYB")', env)
        result2 = eval_source('(lcs-length "GXTXAYB" "AGGTAB")', env)
        assert result1 == result2 == 4

    def test_long_strings(self):
        """Test LCS with longer strings."""
        env = make_global_env()
        result = eval_source('(lcs-length "AGGTAB" "GXTXAYB")', env)
        assert result == 4
