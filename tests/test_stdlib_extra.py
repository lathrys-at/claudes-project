"""Tests for extended standard library functions."""
import pytest
from pebble.evaluator import eval_source, make_global_env, EvalError
from pebble.types import PebbleList, NIL


class TestSort:
    """Tests for the sort function."""

    def test_sort_numbers_ascending(self):
        env = make_global_env()
        result = eval_source("(sort (list 3 1 4 1 5 9 2 6))", env)
        assert list(result) == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_sort_empty_list(self):
        env = make_global_env()
        result = eval_source("(sort (list))", env)
        assert result == NIL

    def test_sort_single_element(self):
        env = make_global_env()
        result = eval_source("(sort (list 42))", env)
        assert list(result) == [42]

    def test_sort_with_duplicates(self):
        env = make_global_env()
        result = eval_source("(sort (list 5 5 1 1 3 3))", env)
        assert list(result) == [1, 1, 3, 3, 5, 5]

    def test_sort_with_negative_numbers(self):
        env = make_global_env()
        result = eval_source("(sort (list 3 -1 0 -5 2))", env)
        assert list(result) == [-5, -1, 0, 2, 3]

    def test_sort_immutability(self):
        env = make_global_env()
        eval_source("""
            (define original (list 3 1 2))
            (define sorted (sort original))
        """, env)
        original = eval_source("original", env)
        assert list(original) == [3, 1, 2]

    def test_sort_strings_lexicographically(self):
        env = make_global_env()
        result = eval_source('(sort (list "zebra" "apple" "banana"))', env)
        assert list(result) == ["apple", "banana", "zebra"]

    def test_sort_already_sorted(self):
        env = make_global_env()
        result = eval_source("(sort (list 1 2 3 4 5))", env)
        assert list(result) == [1, 2, 3, 4, 5]

    def test_sort_reverse_sorted(self):
        env = make_global_env()
        result = eval_source("(sort (list 5 4 3 2 1))", env)
        assert list(result) == [1, 2, 3, 4, 5]


class TestSortWith:
    """Tests for the sort-with function."""

    def test_sort_with_descending_order(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (> a b)) (list 3 1 4 1 5 9 2 6))
        """, env)
        assert list(result) == [9, 6, 5, 4, 3, 2, 1, 1]

    def test_sort_with_ascending_order(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (< a b)) (list 3 1 4 1 5 9 2 6))
        """, env)
        assert list(result) == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_sort_with_absolute_value(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (< (abs a) (abs b))) (list 5 -3 4 -1 2))
        """, env)
        # Sorted by absolute value: -1, 2, -3, 4, 5
        assert list(result) == [-1, 2, -3, 4, 5]

    def test_sort_with_empty_list(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (< a b)) (list))
        """, env)
        assert result == NIL

    def test_sort_with_single_element(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (< a b)) (list 42))
        """, env)
        assert list(result) == [42]

    def test_sort_stability(self):
        """Test that sort is stable: equal elements retain original order."""
        env = make_global_env()
        # Create a list of pairs (lists), sort by first element
        result = eval_source("""
            (define data (list (list 2 "a") (list 1 "b") (list 2 "c") (list 1 "d")))
            (sort-with (lambda (x y) (< (car x) (car y))) data)
        """, env)
        result_list = [list(x) for x in result]
        # Should be: (1 "b"), (1 "d"), (2 "a"), (2 "c")
        # The pairs with equal first elements should keep their original relative order
        assert result_list == [[1, "b"], [1, "d"], [2, "a"], [2, "c"]]

    def test_sort_large_list_ascending(self):
        """Test that sort handles a large list efficiently without stack overflow."""
        env = make_global_env()
        # Create a reverse-sorted list of 1500 elements
        result = eval_source("""
            (define reverse-sorted (reverse (range 1500)))
            (sort reverse-sorted)
        """, env)
        expected = list(range(1500))
        assert list(result) == expected

    def test_sort_large_list_already_sorted(self):
        """Test that sort handles an already-sorted large list efficiently."""
        env = make_global_env()
        # Create an ascending list of 1500 elements
        result = eval_source("""
            (define ascending (range 1500))
            (sort ascending)
        """, env)
        expected = list(range(1500))
        assert list(result) == expected

    def test_sort_large_list_with_sort_with(self):
        """Test that sort-with handles a large list efficiently."""
        env = make_global_env()
        # Create a forward-sorted list and sort it descending
        result = eval_source("""
            (sort-with (lambda (a b) (> a b)) (range 1500))
        """, env)
        expected = list(range(1499, -1, -1))
        assert list(result) == expected


class TestAssoc:
    """Tests for the assoc function."""

    def test_assoc_found(self):
        env = make_global_env()
        result = eval_source("""
            (assoc "x" (list (list "x" 1) (list "y" 2)))
        """, env)
        assert list(result) == ["x", 1]

    def test_assoc_not_found(self):
        env = make_global_env()
        result = eval_source("""
            (assoc "z" (list (list "x" 1) (list "y" 2)))
        """, env)
        assert result is False

    def test_assoc_empty_list(self):
        env = make_global_env()
        result = eval_source("""
            (assoc "x" (list))
        """, env)
        assert result is False

    def test_assoc_first_of_duplicates(self):
        env = make_global_env()
        result = eval_source("""
            (assoc "x" (list (list "x" 1) (list "x" 2)))
        """, env)
        # Should return first match
        assert list(result) == ["x", 1]

    def test_assoc_with_numeric_keys(self):
        env = make_global_env()
        result = eval_source("""
            (assoc 42 (list (list 1 "a") (list 42 "b") (list 99 "c")))
        """, env)
        assert list(result) == [42, "b"]


class TestContains:
    """Tests for the contains? function."""

    def test_contains_present(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 3 4) 3)", env)
        assert result is True

    def test_contains_not_present(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 3 4) 5)", env)
        assert result is False

    def test_contains_empty_list(self):
        env = make_global_env()
        result = eval_source("(contains? (list) 1)", env)
        assert result is False

    def test_contains_first_element(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 3) 1)", env)
        assert result is True

    def test_contains_last_element(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 3) 3)", env)
        assert result is True

    def test_contains_with_strings(self):
        env = make_global_env()
        result = eval_source('(contains? (list "a" "b" "c") "b")', env)
        assert result is True

    def test_contains_with_duplicates(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 1 3) 1)", env)
        assert result is True


class TestIndexOf:
    """Tests for the index-of function."""

    def test_index_of_found_first(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 3 4) 3)", env)
        assert result == 2

    def test_index_of_found_zero(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 3 4) 1)", env)
        assert result == 0

    def test_index_of_not_found(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 3 4) 5)", env)
        assert result == -1

    def test_index_of_empty_list(self):
        env = make_global_env()
        result = eval_source("(index-of (list) 1)", env)
        assert result == -1

    def test_index_of_first_of_duplicates(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 1 3) 1)", env)
        # Should return first occurrence
        assert result == 0

    def test_index_of_with_strings(self):
        env = make_global_env()
        result = eval_source('(index-of (list "a" "b" "c") "b")', env)
        assert result == 1

    def test_index_of_last_element(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 3 4 5) 5)", env)
        assert result == 4


class TestMaximum:
    """Tests for the maximum function."""

    def test_maximum_basic(self):
        env = make_global_env()
        result = eval_source("(maximum (list 1 5 3 2 4))", env)
        assert result == 5

    def test_maximum_single_element(self):
        env = make_global_env()
        result = eval_source("(maximum (list 42))", env)
        assert result == 42

    def test_maximum_with_negatives(self):
        env = make_global_env()
        result = eval_source("(maximum (list -1 -5 -3))", env)
        assert result == -1

    def test_maximum_with_duplicates(self):
        env = make_global_env()
        result = eval_source("(maximum (list 5 5 5))", env)
        assert result == 5

    def test_maximum_empty_list_raises_error(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="maximum: empty list"):
            eval_source("(maximum (list))", env)

    def test_maximum_with_floats(self):
        env = make_global_env()
        result = eval_source("(maximum (list 1.5 2.7 0.3))", env)
        assert result == 2.7


class TestMinimum:
    """Tests for the minimum function."""

    def test_minimum_basic(self):
        env = make_global_env()
        result = eval_source("(minimum (list 5 1 3 2 4))", env)
        assert result == 1

    def test_minimum_single_element(self):
        env = make_global_env()
        result = eval_source("(minimum (list 42))", env)
        assert result == 42

    def test_minimum_with_negatives(self):
        env = make_global_env()
        result = eval_source("(minimum (list -1 -5 -3))", env)
        assert result == -5

    def test_minimum_with_duplicates(self):
        env = make_global_env()
        result = eval_source("(minimum (list 5 5 5))", env)
        assert result == 5

    def test_minimum_empty_list_raises_error(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="minimum: empty list"):
            eval_source("(minimum (list))", env)

    def test_minimum_with_floats(self):
        env = make_global_env()
        result = eval_source("(minimum (list 1.5 2.7 0.3))", env)
        assert result == 0.3


class TestRepeat:
    """Tests for the repeat function."""

    def test_repeat_basic(self):
        env = make_global_env()
        result = eval_source("(repeat 42 3)", env)
        assert list(result) == [42, 42, 42]

    def test_repeat_zero(self):
        env = make_global_env()
        result = eval_source("(repeat 42 0)", env)
        assert result == NIL

    def test_repeat_one(self):
        env = make_global_env()
        result = eval_source("(repeat 42 1)", env)
        assert list(result) == [42]

    def test_repeat_string(self):
        env = make_global_env()
        result = eval_source('(repeat "x" 5)', env)
        assert list(result) == ["x", "x", "x", "x", "x"]

    def test_repeat_list(self):
        env = make_global_env()
        result = eval_source("(repeat (list 1 2) 2)", env)
        assert len(result) == 2
        assert list(result[0]) == [1, 2]
        assert list(result[1]) == [1, 2]

    def test_repeat_large_n(self):
        env = make_global_env()
        result = eval_source("(repeat 1 100)", env)
        assert len(result) == 100
        assert all(x == 1 for x in result)


class TestStringSplit:
    """Tests for the string-split function."""

    def test_string_split_basic(self):
        env = make_global_env()
        result = eval_source('(string-split "a,b,c" ",")', env)
        assert list(result) == ["a", "b", "c"]

    def test_string_split_consecutive_separators(self):
        env = make_global_env()
        result = eval_source('(string-split "a,,c" ",")', env)
        assert list(result) == ["a", "", "c"]

    def test_string_split_separator_not_present(self):
        env = make_global_env()
        result = eval_source('(string-split "abc" ",")', env)
        assert list(result) == ["abc"]

    def test_string_split_empty_string(self):
        env = make_global_env()
        result = eval_source('(string-split "" ",")', env)
        assert list(result) == [""]

    def test_string_split_leading_separator(self):
        env = make_global_env()
        result = eval_source('(string-split ",a" ",")', env)
        assert list(result) == ["", "a"]

    def test_string_split_trailing_separator(self):
        env = make_global_env()
        result = eval_source('(string-split "a," ",")', env)
        assert list(result) == ["a", ""]

    def test_string_split_multi_char_separator(self):
        env = make_global_env()
        result = eval_source('(string-split "a::b::c" "::")', env)
        assert list(result) == ["a", "b", "c"]

    def test_string_split_space_separator(self):
        env = make_global_env()
        result = eval_source('(string-split "hello world test" " ")', env)
        assert list(result) == ["hello", "world", "test"]

    def test_string_split_multi_char_consecutive(self):
        env = make_global_env()
        result = eval_source('(string-split "a::::b" "::")', env)
        assert list(result) == ["a", "", "b"]

    def test_string_split_only_separator(self):
        env = make_global_env()
        result = eval_source('(string-split "," ",")', env)
        assert list(result) == ["", ""]

    def test_string_split_multiple_consecutive_separators(self):
        env = make_global_env()
        result = eval_source('(string-split "a,,,b" ",")', env)
        assert list(result) == ["a", "", "", "b"]
