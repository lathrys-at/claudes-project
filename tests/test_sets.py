"""Tests for list-based set operations: unique, union, intersection, difference."""
import pytest
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList, NIL


class TestUnique:
    """Tests for the unique function."""

    def test_unique_basic(self):
        env = make_global_env()
        result = eval_source("(unique (list 1 2 2 3 1 4))", env)
        expected = PebbleList([1, 2, 3, 4])
        assert result == expected

    def test_unique_empty_list(self):
        env = make_global_env()
        result = eval_source("(unique nil)", env)
        assert result == NIL

    def test_unique_single_element(self):
        env = make_global_env()
        result = eval_source("(unique (list 5))", env)
        expected = PebbleList([5])
        assert result == expected

    def test_unique_strings(self):
        env = make_global_env()
        result = eval_source('(unique (list "a" "b" "a" "c" "b"))', env)
        expected = PebbleList(["a", "b", "c"])
        assert result == expected

    def test_unique_no_duplicates(self):
        env = make_global_env()
        result = eval_source("(unique (list 1 2 3 4))", env)
        expected = PebbleList([1, 2, 3, 4])
        assert result == expected

    def test_unique_all_duplicates(self):
        env = make_global_env()
        result = eval_source("(unique (list 1 1 1 1))", env)
        expected = PebbleList([1])
        assert result == expected

    def test_unique_preserves_order(self):
        env = make_global_env()
        result = eval_source("(unique (list 3 1 4 1 5 9 2 6 5 3))", env)
        expected = PebbleList([3, 1, 4, 5, 9, 2, 6])
        assert result == expected


class TestUnion:
    """Tests for the union function."""

    def test_union_basic(self):
        env = make_global_env()
        result = eval_source("(union (list 1 2 3) (list 3 4 5))", env)
        expected = PebbleList([1, 2, 3, 4, 5])
        assert result == expected

    def test_union_with_duplicates_in_input(self):
        env = make_global_env()
        result = eval_source("(union (list 1 1 2) (list 2 3))", env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_union_empty_first(self):
        env = make_global_env()
        result = eval_source("(union nil (list 1 2 3))", env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_union_empty_second(self):
        env = make_global_env()
        result = eval_source("(union (list 1 2 3) nil)", env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_union_both_empty(self):
        env = make_global_env()
        result = eval_source("(union nil nil)", env)
        assert result == NIL

    def test_union_no_overlap(self):
        env = make_global_env()
        result = eval_source("(union (list 1 2) (list 3 4))", env)
        expected = PebbleList([1, 2, 3, 4])
        assert result == expected

    def test_union_complete_overlap(self):
        env = make_global_env()
        result = eval_source("(union (list 1 2 3) (list 1 2 3))", env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_union_preserves_order_from_a_first(self):
        env = make_global_env()
        result = eval_source("(union (list 3 1 2) (list 4 1 5))", env)
        expected = PebbleList([3, 1, 2, 4, 5])
        assert result == expected


class TestIntersection:
    """Tests for the intersection function."""

    def test_intersection_basic(self):
        env = make_global_env()
        result = eval_source("(intersection (list 1 2 3 4) (list 2 4 6))", env)
        expected = PebbleList([2, 4])
        assert result == expected

    def test_intersection_no_overlap(self):
        env = make_global_env()
        result = eval_source("(intersection (list 1 2) (list 3 4))", env)
        assert result == NIL

    def test_intersection_empty_first(self):
        env = make_global_env()
        result = eval_source("(intersection nil (list 1 2 3))", env)
        assert result == NIL

    def test_intersection_empty_second(self):
        env = make_global_env()
        result = eval_source("(intersection (list 1 2 3) nil)", env)
        assert result == NIL

    def test_intersection_both_empty(self):
        env = make_global_env()
        result = eval_source("(intersection nil nil)", env)
        assert result == NIL

    def test_intersection_complete_overlap(self):
        env = make_global_env()
        result = eval_source("(intersection (list 1 2 3) (list 1 2 3))", env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_intersection_with_duplicates_in_a(self):
        env = make_global_env()
        result = eval_source("(intersection (list 1 2 2 3) (list 2 3 4))", env)
        expected = PebbleList([2, 3])
        assert result == expected

    def test_intersection_with_duplicates_in_b(self):
        env = make_global_env()
        result = eval_source("(intersection (list 1 2 3) (list 2 2 3 3))", env)
        expected = PebbleList([2, 3])
        assert result == expected

    def test_intersection_preserves_a_order(self):
        env = make_global_env()
        result = eval_source("(intersection (list 4 2 3 1) (list 1 2 3 4))", env)
        expected = PebbleList([4, 2, 3, 1])
        assert result == expected


class TestDifference:
    """Tests for the difference function."""

    def test_difference_basic(self):
        env = make_global_env()
        result = eval_source("(difference (list 1 2 3 4) (list 2 4))", env)
        expected = PebbleList([1, 3])
        assert result == expected

    def test_difference_no_elements_in_b(self):
        env = make_global_env()
        result = eval_source("(difference (list 1 2 3) (list 4 5 6))", env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_difference_all_elements_in_b(self):
        env = make_global_env()
        result = eval_source("(difference (list 1 2) (list 1 2))", env)
        assert result == NIL

    def test_difference_empty_first(self):
        env = make_global_env()
        result = eval_source("(difference nil (list 1 2 3))", env)
        assert result == NIL

    def test_difference_empty_second(self):
        env = make_global_env()
        result = eval_source("(difference (list 1 2 3) nil)", env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_difference_both_empty(self):
        env = make_global_env()
        result = eval_source("(difference nil nil)", env)
        assert result == NIL

    def test_difference_with_duplicates_in_a(self):
        env = make_global_env()
        result = eval_source("(difference (list 1 1 2 3) (list 2))", env)
        expected = PebbleList([1, 3])
        assert result == expected

    def test_difference_with_duplicates_in_b(self):
        env = make_global_env()
        result = eval_source("(difference (list 1 2 3) (list 2 2 2))", env)
        expected = PebbleList([1, 3])
        assert result == expected

    def test_difference_preserves_order(self):
        env = make_global_env()
        result = eval_source("(difference (list 4 2 3 1) (list 2))", env)
        expected = PebbleList([4, 3, 1])
        assert result == expected


class TestSetOperationsWithSymbols:
    """Tests for set operations with symbols as elements."""

    def test_unique_symbols(self):
        env = make_global_env()
        result = eval_source("(unique (list 'a 'b 'a 'c))", env)
        # Note: symbols are represented with Symbol type
        assert len(result) == 3

    def test_union_symbols(self):
        env = make_global_env()
        result = eval_source("(union (list 'a 'b) (list 'b 'c))", env)
        assert len(result) == 3

    def test_intersection_symbols(self):
        env = make_global_env()
        result = eval_source("(intersection (list 'a 'b 'c) (list 'b 'c 'd))", env)
        assert len(result) == 2

    def test_difference_symbols(self):
        env = make_global_env()
        result = eval_source("(difference (list 'a 'b 'c) (list 'b))", env)
        assert len(result) == 2


class TestStackSafety:
    """Tests for stack-safety on large lists."""

    def test_unique_large_list(self):
        """Test that unique handles large lists without RecursionError."""
        env = make_global_env()
        # Create a list of 200 elements, repeated twice, and check unique length
        result = eval_source(
            "(length (unique (append (range 200) (range 200))))",
            env
        )
        assert result == 200

    def test_union_large_lists(self):
        """Test that union handles large lists without RecursionError."""
        env = make_global_env()
        result = eval_source(
            "(length (union (range 40) (range 40 80)))",
            env
        )
        assert result == 80

    def test_intersection_large_lists(self):
        """Test that intersection handles large lists without RecursionError."""
        env = make_global_env()
        result = eval_source(
            "(length (intersection (range 200) (range 100 300)))",
            env
        )
        assert result == 100

    def test_difference_large_lists(self):
        """Test that difference handles large lists without RecursionError."""
        env = make_global_env()
        result = eval_source(
            "(length (difference (range 200) (range 50 150)))",
            env
        )
        assert result == 100


class TestEdgeCases:
    """Tests for edge cases and interactions."""

    def test_nested_set_operations(self):
        env = make_global_env()
        result = eval_source(
            "(union (intersection (list 1 2 3 4) (list 2 3 4 5)) (list 5 6))",
            env
        )
        expected = PebbleList([2, 3, 4, 5, 6])
        assert result == expected

    def test_unique_after_union(self):
        env = make_global_env()
        result = eval_source(
            "(unique (union (list 1 2 1) (list 2 3 2)))",
            env
        )
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_difference_after_union(self):
        env = make_global_env()
        result = eval_source(
            "(difference (union (list 1 2) (list 3 4)) (list 2 3))",
            env
        )
        expected = PebbleList([1, 4])
        assert result == expected
