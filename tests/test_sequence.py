"""Tests for sequence generation functions: iterate and range-step."""

import pytest
from pebble.reader import read_one
from pebble.evaluator import make_global_env, seval, EvalError


class TestIterate:
    """Tests for the iterate function."""

    def test_iterate_double_five_elements(self):
        """Test: (iterate (lambda (v) (* v 2)) 1 5) -> (1 2 4 8 16)"""
        env = make_global_env()
        expr = read_one("(iterate (lambda (v) (* v 2)) 1 5)")
        result = seval(expr, env)
        expected_expr = read_one("(list 1 2 4 8 16)")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_iterate_inc_three(self):
        """Test: (iterate inc 10 3) -> (10 11 12)"""
        env = make_global_env()
        expr = read_one("(iterate inc 10 3)")
        result = seval(expr, env)
        expected_expr = read_one("(list 10 11 12)")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_iterate_zero_elements(self):
        """Test: (iterate inc 0 0) -> nil"""
        env = make_global_env()
        expr = read_one("(iterate inc 0 0)")
        result = seval(expr, env)
        expected_expr = read_one("nil")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_iterate_one_element(self):
        """Test: (iterate inc 7 1) -> (7)"""
        env = make_global_env()
        expr = read_one("(iterate inc 7 1)")
        result = seval(expr, env)
        expected_expr = read_one("(list 7)")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_iterate_large_n_stack_safe(self):
        """Test that iterate is stack-safe for large n (4000 elements)."""
        env = make_global_env()
        expr = read_one("(length (iterate inc 0 4000))")
        result = seval(expr, env)
        assert result == 4000


class TestRangeStep:
    """Tests for the range-step function."""

    def test_range_step_positive_0_10_2(self):
        """Test: (range-step 0 10 2) -> (0 2 4 6 8)"""
        env = make_global_env()
        expr = read_one("(range-step 0 10 2)")
        result = seval(expr, env)
        expected_expr = read_one("(list 0 2 4 6 8)")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_range_step_positive_1_10_3(self):
        """Test: (range-step 1 10 3) -> (1 4 7)"""
        env = make_global_env()
        expr = read_one("(range-step 1 10 3)")
        result = seval(expr, env)
        expected_expr = read_one("(list 1 4 7)")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_range_step_positive_0_5_1(self):
        """Test: (range-step 0 5 1) -> (0 1 2 3 4)"""
        env = make_global_env()
        expr = read_one("(range-step 0 5 1)")
        result = seval(expr, env)
        expected_expr = read_one("(list 0 1 2 3 4)")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_range_step_negative_10_0_minus_2(self):
        """Test: (range-step 10 0 -2) -> (10 8 6 4 2)"""
        env = make_global_env()
        expr = read_one("(range-step 10 0 -2)")
        result = seval(expr, env)
        expected_expr = read_one("(list 10 8 6 4 2)")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_range_step_equal_start_stop(self):
        """Test: (range-step 5 5 1) -> nil (exclusive endpoint)"""
        env = make_global_env()
        expr = read_one("(range-step 5 5 1)")
        result = seval(expr, env)
        expected_expr = read_one("nil")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_range_step_negative_step_ascending_range(self):
        """Test: (range-step 0 10 -1) -> nil (negative step but start < stop)"""
        env = make_global_env()
        expr = read_one("(range-step 0 10 -1)")
        result = seval(expr, env)
        expected_expr = read_one("nil")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_range_step_single_element(self):
        """Test: (range-step 0 1 1) -> (0)"""
        env = make_global_env()
        expr = read_one("(range-step 0 1 1)")
        result = seval(expr, env)
        expected_expr = read_one("(list 0)")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_range_step_zero_equals_zero(self):
        """Test: (range-step 0 0 5) -> nil"""
        env = make_global_env()
        expr = read_one("(range-step 0 0 5)")
        result = seval(expr, env)
        expected_expr = read_one("nil")
        expected = seval(expected_expr, env)
        assert result == expected

    def test_range_step_zero_step_error(self):
        """Test: (range-step 0 10 0) raises EvalError"""
        env = make_global_env()
        expr = read_one("(range-step 0 10 0)")
        with pytest.raises(EvalError, match="step must be nonzero"):
            seval(expr, env)

    def test_range_step_large_positive_stack_safe(self):
        """Test that range-step is stack-safe for large ranges (4000 elements)."""
        env = make_global_env()
        expr = read_one("(length (range-step 0 4000 1))")
        result = seval(expr, env)
        assert result == 4000
