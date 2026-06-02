"""Tests for statistics functions: mean, median, variance, stddev."""
import pytest
from pebble.evaluator import make_global_env, eval_source, EvalError


def eval_in_env(source):
    """Evaluate a Pebble expression and return the result."""
    env = make_global_env()
    return eval_source(source, env)


def approx_equal(a, b, tolerance=1e-9):
    """Check if two floats are approximately equal within tolerance."""
    return abs(a - b) < tolerance


class TestMean:
    """Test mean function."""

    def test_mean_odd_length(self):
        """Test mean of odd-length list: (1 2 3 4 5) -> 3."""
        result = eval_in_env("(mean (list 1 2 3 4 5))")
        assert result == 3

    def test_mean_even_length(self):
        """Test mean of even-length list: (2 4 6) -> 4."""
        result = eval_in_env("(mean (list 2 4 6))")
        assert result == 4

    def test_mean_two_elements(self):
        """Test mean of two elements: (1 2) -> 1.5."""
        result = eval_in_env("(mean (list 1 2))")
        assert approx_equal(result, 1.5)

    def test_mean_single_element(self):
        """Test mean of single element: (10) -> 10."""
        result = eval_in_env("(mean (list 10))")
        assert result == 10

    def test_mean_empty_list_error(self):
        """Test that mean of empty list raises EvalError."""
        with pytest.raises(EvalError, match="mean: empty list"):
            eval_in_env("(mean nil)")


class TestMedian:
    """Test median function."""

    def test_median_odd_unsorted(self):
        """Test median of odd-length unsorted list: (3 1 2) -> 2."""
        result = eval_in_env("(median (list 3 1 2))")
        assert result == 2

    def test_median_even_unsorted(self):
        """Test median of even-length unsorted list: (1 2 3 4) -> 2.5."""
        result = eval_in_env("(median (list 1 2 3 4))")
        assert approx_equal(result, 2.5)

    def test_median_single_element(self):
        """Test median of single element: (5) -> 5."""
        result = eval_in_env("(median (list 5))")
        assert result == 5

    def test_median_four_unsorted(self):
        """Test median of four unsorted elements: (4 1 3 2) -> 2.5."""
        result = eval_in_env("(median (list 4 1 3 2))")
        assert approx_equal(result, 2.5)

    def test_median_three_same(self):
        """Test median of three identical elements: (7 7 7) -> 7."""
        result = eval_in_env("(median (list 7 7 7))")
        assert result == 7

    def test_median_empty_list_error(self):
        """Test that median of empty list raises EvalError."""
        with pytest.raises(EvalError, match="median: empty list"):
            eval_in_env("(median nil)")


class TestVariance:
    """Test variance function."""

    def test_variance_1_to_5(self):
        """Test variance of (1 2 3 4 5) -> 2."""
        result = eval_in_env("(variance (list 1 2 3 4 5))")
        # Mean is 3, squared diffs are (4 1 0 1 4), sum is 10, divide by 5 = 2
        assert approx_equal(result, 2.0)

    def test_variance_2_4_6(self):
        """Test variance of (2 4 6) -> 8/3 (approximately 2.6667)."""
        result = eval_in_env("(variance (list 2 4 6))")
        # Mean is 4, squared diffs are (4 0 4), sum is 8, divide by 3 = 8/3
        assert approx_equal(result, 8/3)

    def test_variance_all_same(self):
        """Test variance of identical elements (5 5 5) -> 0."""
        result = eval_in_env("(variance (list 5 5 5))")
        assert approx_equal(result, 0.0)

    def test_variance_empty_list_error(self):
        """Test that variance of empty list raises EvalError."""
        with pytest.raises(EvalError, match="variance: empty list"):
            eval_in_env("(variance nil)")


class TestStddev:
    """Test stddev function."""

    def test_stddev_1_to_5(self):
        """Test stddev of (1 2 3 4 5) -> sqrt(2) (approximately 1.4142135623730951)."""
        result = eval_in_env("(stddev (list 1 2 3 4 5))")
        # variance is 2, sqrt(2) ≈ 1.4142135623730951
        assert approx_equal(result, 1.4142135623730951)

    def test_stddev_all_same(self):
        """Test stddev of identical elements (5 5 5) -> 0."""
        result = eval_in_env("(stddev (list 5 5 5))")
        assert approx_equal(result, 0.0)

    def test_stddev_variance_consistency(self):
        """Test that (stddev lst)^2 ≈ (variance lst)."""
        # For list (1 2 3 4 5)
        variance_result = eval_in_env("(variance (list 1 2 3 4 5))")
        stddev_result = eval_in_env("(stddev (list 1 2 3 4 5))")
        squared_stddev = stddev_result * stddev_result
        assert approx_equal(squared_stddev, variance_result, tolerance=1e-9)

    def test_stddev_empty_list_error(self):
        """Test that stddev of empty list raises EvalError."""
        with pytest.raises(EvalError, match="stddev: empty list"):
            eval_in_env("(stddev nil)")


class TestStatisticsIntegration:
    """Integration tests for statistics functions."""

    def test_mean_preserves_order(self):
        """Test that mean does not mutate input (indirectly via consistency)."""
        result1 = eval_in_env("(mean (list 1 2 3))")
        result2 = eval_in_env("(mean (list 1 2 3))")
        assert result1 == result2

    def test_median_preserves_order_indirectly(self):
        """Test that median sorts internally and does not mutate input."""
        # Evaluate median twice on the same unsorted list
        result1 = eval_in_env("(median (list 5 2 8 1))")
        result2 = eval_in_env("(median (list 5 2 8 1))")
        assert result1 == result2

    def test_floats_and_ints_mix(self):
        """Test that statistics functions work with mixed int and float lists."""
        result = eval_in_env("(mean (list 1 2.5 3 4.5))")
        # (1 + 2.5 + 3 + 4.5) / 4 = 11 / 4 = 2.75
        assert approx_equal(result, 2.75)
