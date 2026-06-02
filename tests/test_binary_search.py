"""Tests for binary-search function in the standard library."""

import pytest
from pebble.evaluator import eval_source, make_global_env


class TestBinarySearchFound:
    """Tests for binary-search when the target IS found."""

    def test_found_at_middle(self):
        """Find element at middle position."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 1 3 5 7 9) 5)", env)
        assert result == 2

    def test_found_at_start(self):
        """Find element at start (index 0)."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 1 3 5 7 9) 1)", env)
        assert result == 0

    def test_found_at_end(self):
        """Find element at end (last index)."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 1 3 5 7 9) 9)", env)
        assert result == 4

    def test_found_at_position_three(self):
        """Find element at another position."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 1 3 5 7 9) 7)", env)
        assert result == 3

    def test_single_element_found(self):
        """Find single element in vector of length 1."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 42) 42)", env)
        assert result == 0

    def test_even_length_vector(self):
        """Find element in even-length vector."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 2 4 6 8) 6)", env)
        assert result == 2


class TestBinarySearchNotFound:
    """Tests for binary-search when the target is NOT found."""

    def test_not_found_in_gap(self):
        """Target not found when it would be in a gap between elements."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 1 3 5 7 9) 4)", env)
        assert result == -1

    def test_not_found_below_range(self):
        """Target not found when it's below all elements."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 1 3 5 7 9) 0)", env)
        assert result == -1

    def test_not_found_above_range(self):
        """Target not found when it's above all elements."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 1 3 5 7 9) 10)", env)
        assert result == -1

    def test_single_element_not_found(self):
        """Target not found in single-element vector."""
        env = make_global_env()
        result = eval_source("(binary-search (vector 42) 7)", env)
        assert result == -1


class TestBinarySearchEdgeCases:
    """Tests for edge cases."""

    def test_empty_vector(self):
        """Empty vector always returns -1."""
        env = make_global_env()
        result = eval_source("(binary-search (vector) 5)", env)
        assert result == -1

    def test_large_vector_found(self):
        """Find element in large vector (range 1000)."""
        env = make_global_env()
        result = eval_source("(binary-search (list->vector (range 1000)) 777)", env)
        assert result == 777

    def test_large_vector_first_element(self):
        """Find first element in large vector."""
        env = make_global_env()
        result = eval_source("(binary-search (list->vector (range 1000)) 0)", env)
        assert result == 0

    def test_large_vector_last_element(self):
        """Find last element in large vector."""
        env = make_global_env()
        result = eval_source("(binary-search (list->vector (range 1000)) 999)", env)
        assert result == 999

    def test_large_vector_not_found(self):
        """Element not found in large vector."""
        env = make_global_env()
        result = eval_source("(binary-search (list->vector (range 1000)) 1000)", env)
        assert result == -1
