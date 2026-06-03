"""Tests for list utility functions: rotate, interpose, count"""
import pytest
from pebble.evaluator import make_global_env, eval_source


class TestRotate:
    """Test the rotate function"""

    def setup_method(self):
        self.env = make_global_env()

    def test_rotate_basic(self):
        """Test basic rotation by 2 positions"""
        code = "(rotate (list 1 2 3 4 5) 2)"
        result = eval_source(code, self.env)
        expected = [3, 4, 5, 1, 2]
        assert list(result) == expected

    def test_rotate_zero(self):
        """Test rotation by 0 positions returns unchanged list"""
        code = "(rotate (list 1 2 3) 0)"
        result = eval_source(code, self.env)
        expected = [1, 2, 3]
        assert list(result) == expected

    def test_rotate_full_rotation(self):
        """Test rotation by list length returns unchanged list"""
        code = "(rotate (list 1 2 3) 3)"
        result = eval_source(code, self.env)
        expected = [1, 2, 3]
        assert list(result) == expected

    def test_rotate_wrap_around(self):
        """Test rotation with n > length (4 mod 3 = 1)"""
        code = "(rotate (list 1 2 3) 4)"
        result = eval_source(code, self.env)
        expected = [2, 3, 1]
        assert list(result) == expected

    def test_rotate_single_element(self):
        """Test rotation of single element list"""
        code = "(rotate (list 1) 5)"
        result = eval_source(code, self.env)
        expected = [1]
        assert list(result) == expected

    def test_rotate_empty_list(self):
        """Test rotation of empty list"""
        code = "(rotate nil 2)"
        result = eval_source(code, self.env)
        assert list(result) == []


class TestInterpose:
    """Test the interpose function"""

    def setup_method(self):
        self.env = make_global_env()

    def test_interpose_basic(self):
        """Test basic interpose with numeric elements"""
        code = "(interpose 0 (list 1 2 3))"
        result = eval_source(code, self.env)
        expected = [1, 0, 2, 0, 3]
        assert list(result) == expected

    def test_interpose_two_elements(self):
        """Test interpose with two elements"""
        code = "(interpose 0 (list 1 2))"
        result = eval_source(code, self.env)
        expected = [1, 0, 2]
        assert list(result) == expected

    def test_interpose_one_element(self):
        """Test interpose with one element"""
        code = "(interpose 0 (list 1))"
        result = eval_source(code, self.env)
        expected = [1]
        assert list(result) == expected

    def test_interpose_empty_list(self):
        """Test interpose with empty list"""
        code = "(interpose 0 nil)"
        result = eval_source(code, self.env)
        assert list(result) == []

    def test_interpose_strings(self):
        """Test interpose with string elements"""
        code = '(interpose "," (list "a" "b" "c"))'
        result = eval_source(code, self.env)
        expected = ["a", ",", "b", ",", "c"]
        assert list(result) == expected


class TestCount:
    """Test the count function"""

    def setup_method(self):
        self.env = make_global_env()

    def test_count_basic(self):
        """Test basic count of element occurrences"""
        code = "(count 2 (list 1 2 2 3 2))"
        result = eval_source(code, self.env)
        assert result == 3

    def test_count_not_found(self):
        """Test count when element is not found"""
        code = "(count 5 (list 1 2 3))"
        result = eval_source(code, self.env)
        assert result == 0

    def test_count_empty_list(self):
        """Test count on empty list"""
        code = "(count 1 nil)"
        result = eval_source(code, self.env)
        assert result == 0

    def test_count_strings(self):
        """Test count with string elements"""
        code = '(count "a" (list "a" "b" "a"))'
        result = eval_source(code, self.env)
        assert result == 2

    def test_count_large_list_stack_safe(self):
        """Test count on large list to verify stack safety"""
        # Create a list of 3000 elements (all zeros)
        code = "(count 0 (range 3000))"
        result = eval_source(code, self.env)
        # range 3000 produces (0 1 2 ... 2999), so count of 0 should be 1
        assert result == 1

    def test_count_large_list_not_found(self):
        """Test count on large list where element is not found"""
        # Create a list of 3000 elements (0..2999), counting 7 which doesn't exist at start
        code = "(count 7 (range 3000))"
        result = eval_source(code, self.env)
        # range 3000 produces (0 1 2 ... 2999), so count of 7 should be 1 (7 is in the list)
        assert result == 1

    def test_count_large_list_not_in_range(self):
        """Test count on large list where element is definitely not found"""
        code = "(count 5000 (range 3000))"
        result = eval_source(code, self.env)
        # range 3000 produces (0 1 2 ... 2999), so count of 5000 should be 0
        assert result == 0
