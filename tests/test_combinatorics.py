"""Tests for combinatorics functions: factorial, permutations-count, combinations-count"""
import pytest
from pebble.evaluator import make_global_env, eval_source


class TestFactorial:
    """Test factorial function"""

    def test_factorial_0(self):
        env = make_global_env()
        result = eval_source("(factorial 0)", env)
        assert result == 1

    def test_factorial_1(self):
        env = make_global_env()
        result = eval_source("(factorial 1)", env)
        assert result == 1

    def test_factorial_5(self):
        env = make_global_env()
        result = eval_source("(factorial 5)", env)
        assert result == 120

    def test_factorial_10(self):
        env = make_global_env()
        result = eval_source("(factorial 10)", env)
        assert result == 3628800

    def test_factorial_13_big_integer(self):
        """Test big integer case: 13! = 6227020800"""
        env = make_global_env()
        result = eval_source("(factorial 13)", env)
        assert result == 6227020800

    def test_factorial_negative_raises_error(self):
        env = make_global_env()
        with pytest.raises(Exception) as exc_info:
            eval_source("(factorial -1)", env)
        assert "non-negative" in str(exc_info.value).lower()

    def test_factorial_non_integer_raises_error(self):
        env = make_global_env()
        with pytest.raises(Exception) as exc_info:
            eval_source("(factorial 3.14)", env)
        assert "integer" in str(exc_info.value).lower()


class TestCombinationsCount:
    """Test combinations-count function"""

    def test_combinations_count_5_2(self):
        """C(5,2) = 10"""
        env = make_global_env()
        result = eval_source("(combinations-count 5 2)", env)
        assert result == 10

    def test_combinations_count_5_0(self):
        """C(5,0) = 1"""
        env = make_global_env()
        result = eval_source("(combinations-count 5 0)", env)
        assert result == 1

    def test_combinations_count_5_5(self):
        """C(5,5) = 1"""
        env = make_global_env()
        result = eval_source("(combinations-count 5 5)", env)
        assert result == 1

    def test_combinations_count_k_greater_than_n(self):
        """C(5,6) = 0 (k > n)"""
        env = make_global_env()
        result = eval_source("(combinations-count 5 6)", env)
        assert result == 0

    def test_combinations_count_6_3(self):
        """C(6,3) = 20"""
        env = make_global_env()
        result = eval_source("(combinations-count 6 3)", env)
        assert result == 20

    def test_combinations_count_52_5(self):
        """C(52,5) = 2598960"""
        env = make_global_env()
        result = eval_source("(combinations-count 52 5)", env)
        assert result == 2598960

    def test_combinations_count_symmetry(self):
        """C(n,k) == C(n,n-k) for C(6,2) and C(6,4)"""
        env = make_global_env()
        result1 = eval_source("(combinations-count 6 2)", env)
        result2 = eval_source("(combinations-count 6 4)", env)
        assert result1 == result2

    def test_combinations_count_pascal_triangle(self):
        """Verify Pascal's triangle connection: C(n-1,k-1) + C(n-1,k) = C(n,k)"""
        env = make_global_env()
        # C(5,2) = C(4,1) + C(4,2) = 4 + 6 = 10
        c_5_2 = eval_source("(combinations-count 5 2)", env)
        c_4_1 = eval_source("(combinations-count 4 1)", env)
        c_4_2 = eval_source("(combinations-count 4 2)", env)
        assert c_5_2 == c_4_1 + c_4_2

    def test_combinations_count_negative_n_raises_error(self):
        env = make_global_env()
        with pytest.raises(Exception) as exc_info:
            eval_source("(combinations-count -1 2)", env)
        assert "non-negative" in str(exc_info.value).lower()

    def test_combinations_count_negative_k_raises_error(self):
        env = make_global_env()
        with pytest.raises(Exception) as exc_info:
            eval_source("(combinations-count 5 -1)", env)
        assert "non-negative" in str(exc_info.value).lower()


class TestPermutationsCount:
    """Test permutations-count function"""

    def test_permutations_count_5_2(self):
        """P(5,2) = 20"""
        env = make_global_env()
        result = eval_source("(permutations-count 5 2)", env)
        assert result == 20

    def test_permutations_count_5_0(self):
        """P(5,0) = 1"""
        env = make_global_env()
        result = eval_source("(permutations-count 5 0)", env)
        assert result == 1

    def test_permutations_count_5_5(self):
        """P(5,5) = 120 (which is 5!)"""
        env = make_global_env()
        result = eval_source("(permutations-count 5 5)", env)
        assert result == 120

    def test_permutations_count_k_greater_than_n(self):
        """P(5,6) = 0 (k > n)"""
        env = make_global_env()
        result = eval_source("(permutations-count 5 6)", env)
        assert result == 0

    def test_permutations_count_10_3(self):
        """P(10,3) = 720"""
        env = make_global_env()
        result = eval_source("(permutations-count 10 3)", env)
        assert result == 720

    def test_permutations_count_relationship_to_combinations(self):
        """Verify P(n,k) = C(n,k) * k!"""
        env = make_global_env()
        # P(5,2) should equal C(5,2) * 2! = 10 * 2 = 20
        p_5_2 = eval_source("(permutations-count 5 2)", env)
        c_5_2 = eval_source("(combinations-count 5 2)", env)
        factorial_2 = eval_source("(factorial 2)", env)
        assert p_5_2 == c_5_2 * factorial_2

    def test_permutations_count_negative_n_raises_error(self):
        env = make_global_env()
        with pytest.raises(Exception) as exc_info:
            eval_source("(permutations-count -1 2)", env)
        assert "non-negative" in str(exc_info.value).lower()

    def test_permutations_count_negative_k_raises_error(self):
        env = make_global_env()
        with pytest.raises(Exception) as exc_info:
            eval_source("(permutations-count 5 -1)", env)
        assert "non-negative" in str(exc_info.value).lower()
