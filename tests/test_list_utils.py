"""Tests for higher-order list utility functions."""
import pytest
from pebble.evaluator import make_global_env, eval_source, seval
from pebble.reader import read_one
from pebble.types import PebbleList, NIL


class TestTakeWhile:
    """Tests for take-while function."""

    def test_take_while_basic(self):
        """Test take-while with simple predicate."""
        env = make_global_env()
        expr = read_one("(take-while (lambda (x) (< x 3)) (list 1 2 3 4 1))")
        result = seval(expr, env)
        expected = PebbleList([1, 2])
        assert result == expected

    def test_take_while_false_first(self):
        """Test take-while when predicate is false for first element."""
        env = make_global_env()
        expr = read_one("(take-while (lambda (x) (< x 0)) (list 1 2 3))")
        result = seval(expr, env)
        assert result == NIL

    def test_take_while_all_true(self):
        """Test take-while when predicate is true for all elements."""
        env = make_global_env()
        expr = read_one("(take-while (lambda (x) (> x 0)) (list 1 2 3 4))")
        result = seval(expr, env)
        expected = PebbleList([1, 2, 3, 4])
        assert result == expected

    def test_take_while_empty_list(self):
        """Test take-while on empty list."""
        env = make_global_env()
        expr = read_one("(take-while (lambda (x) (< x 3)) nil)")
        result = seval(expr, env)
        assert result == NIL


class TestDropWhile:
    """Tests for drop-while function."""

    def test_drop_while_basic(self):
        """Test drop-while with simple predicate."""
        env = make_global_env()
        expr = read_one("(drop-while (lambda (x) (< x 3)) (list 1 2 3 4 1))")
        result = seval(expr, env)
        expected = PebbleList([3, 4, 1])
        assert result == expected

    def test_drop_while_false_first(self):
        """Test drop-while when predicate is false for first element."""
        env = make_global_env()
        expr = read_one("(drop-while (lambda (x) (< x 0)) (list 1 2 3))")
        result = seval(expr, env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_drop_while_all_true(self):
        """Test drop-while when predicate is true for all elements."""
        env = make_global_env()
        expr = read_one("(drop-while (lambda (x) (> x 0)) (list 1 2 3 4))")
        result = seval(expr, env)
        assert result == NIL

    def test_drop_while_empty_list(self):
        """Test drop-while on empty list."""
        env = make_global_env()
        expr = read_one("(drop-while (lambda (x) (< x 3)) nil)")
        result = seval(expr, env)
        assert result == NIL


class TestFind:
    """Tests for find function."""

    def test_find_found(self):
        """Test find when predicate matches."""
        env = make_global_env()
        expr = read_one("(find even? (list 1 3 4 5))")
        result = seval(expr, env)
        assert result == 4

    def test_find_not_found(self):
        """Test find when predicate doesn't match any element."""
        env = make_global_env()
        expr = read_one("(find even? (list 1 3 5))")
        result = seval(expr, env)
        assert result is False

    def test_find_empty_list(self):
        """Test find on empty list."""
        env = make_global_env()
        expr = read_one("(find even? nil)")
        result = seval(expr, env)
        assert result is False

    def test_find_first_match(self):
        """Test that find returns the first matching element."""
        env = make_global_env()
        expr = read_one("(find even? (list 1 2 3 4 6))")
        result = seval(expr, env)
        assert result == 2


class TestAny:
    """Tests for any? function."""

    def test_any_true_single_match(self):
        """Test any? when predicate matches at least one element."""
        env = make_global_env()
        expr = read_one("(any? even? (list 1 3 4))")
        result = seval(expr, env)
        assert result is True

    def test_any_false_no_match(self):
        """Test any? when predicate matches no elements."""
        env = make_global_env()
        expr = read_one("(any? even? (list 1 3 5))")
        result = seval(expr, env)
        assert result is False

    def test_any_empty_list(self):
        """Test any? on empty list returns false."""
        env = make_global_env()
        expr = read_one("(any? even? nil)")
        result = seval(expr, env)
        assert result is False

    def test_any_all_match(self):
        """Test any? when predicate matches all elements."""
        env = make_global_env()
        expr = read_one("(any? even? (list 2 4 6))")
        result = seval(expr, env)
        assert result is True


class TestAll:
    """Tests for all? function."""

    def test_all_true_all_match(self):
        """Test all? when predicate matches all elements."""
        env = make_global_env()
        expr = read_one("(all? even? (list 2 4 6))")
        result = seval(expr, env)
        assert result is True

    def test_all_false_partial_match(self):
        """Test all? when predicate matches some but not all elements."""
        env = make_global_env()
        expr = read_one("(all? even? (list 2 3))")
        result = seval(expr, env)
        assert result is False

    def test_all_empty_list(self):
        """Test all? on empty list returns true (vacuously)."""
        env = make_global_env()
        expr = read_one("(all? even? nil)")
        result = seval(expr, env)
        assert result is True

    def test_all_no_match(self):
        """Test all? when predicate matches no elements."""
        env = make_global_env()
        expr = read_one("(all? even? (list 1 3 5))")
        result = seval(expr, env)
        assert result is False


class TestCountIf:
    """Tests for count-if function."""

    def test_count_if_basic(self):
        """Test count-if counts matching elements."""
        env = make_global_env()
        expr = read_one("(count-if even? (list 1 2 3 4 5 6))")
        result = seval(expr, env)
        assert result == 3

    def test_count_if_none_match(self):
        """Test count-if when no elements match."""
        env = make_global_env()
        expr = read_one("(count-if even? (list 1 3 5))")
        result = seval(expr, env)
        assert result == 0

    def test_count_if_empty_list(self):
        """Test count-if on empty list returns 0."""
        env = make_global_env()
        expr = read_one("(count-if even? nil)")
        result = seval(expr, env)
        assert result == 0

    def test_count_if_all_match(self):
        """Test count-if when all elements match."""
        env = make_global_env()
        expr = read_one("(count-if even? (list 2 4 6 8))")
        result = seval(expr, env)
        assert result == 4


class TestPartition:
    """Tests for partition function."""

    def test_partition_basic(self):
        """Test partition splits list correctly."""
        env = make_global_env()
        expr = read_one("(partition even? (list 1 2 3 4 5))")
        result = seval(expr, env)
        # Result should be ((2 4) (1 3 5))
        expected = PebbleList([
            PebbleList([2, 4]),
            PebbleList([1, 3, 5])
        ])
        assert result == expected

    def test_partition_empty_list(self):
        """Test partition on empty list."""
        env = make_global_env()
        expr = read_one("(partition even? nil)")
        result = seval(expr, env)
        # Result should be (nil nil)
        expected = PebbleList([NIL, NIL])
        assert result == expected

    def test_partition_all_match(self):
        """Test partition when all elements match predicate."""
        env = make_global_env()
        expr = read_one("(partition even? (list 2 4 6))")
        result = seval(expr, env)
        # Result should be ((2 4 6) nil)
        expected = PebbleList([
            PebbleList([2, 4, 6]),
            NIL
        ])
        assert result == expected

    def test_partition_none_match(self):
        """Test partition when no elements match predicate."""
        env = make_global_env()
        expr = read_one("(partition even? (list 1 3 5))")
        result = seval(expr, env)
        # Result should be (nil (1 3 5))
        expected = PebbleList([
            NIL,
            PebbleList([1, 3, 5])
        ])
        assert result == expected

    def test_partition_preserves_order(self):
        """Test that partition preserves original order in both sublists."""
        env = make_global_env()
        expr = read_one("(partition (lambda (x) (> x 2)) (list 5 1 3 2 4))")
        result = seval(expr, env)
        # Result should be ((5 3 4) (1 2))
        expected = PebbleList([
            PebbleList([5, 3, 4]),
            PebbleList([1, 2])
        ])
        assert result == expected


class TestStackSafety:
    """Tests for stack-safety of list utility functions."""

    def test_count_if_large_list(self):
        """Test count-if is stack-safe on a large list."""
        env = make_global_env()
        # Create a range from 0 to 4999 and count evens (should be 2500)
        expr = read_one("(count-if even? (range 5000))")
        result = seval(expr, env)
        assert result == 2500

    def test_take_while_large_list(self):
        """Test take-while is stack-safe on a large list."""
        env = make_global_env()
        # Take while x < 4000 from range 5000, should get 4000 elements
        expr = read_one("(length (take-while (lambda (x) (< x 4000)) (range 5000)))")
        result = seval(expr, env)
        assert result == 4000

    def test_drop_while_large_list(self):
        """Test drop-while is stack-safe on a large list."""
        env = make_global_env()
        # Drop while x < 4000 from range 5000, should get 1000 elements (4000-4999)
        expr = read_one("(length (drop-while (lambda (x) (< x 4000)) (range 5000)))")
        result = seval(expr, env)
        assert result == 1000

    def test_any_large_list(self):
        """Test any? is stack-safe on a large list."""
        env = make_global_env()
        # Check if any element is even in a range 5000 (first element is 0, which is even)
        expr = read_one("(any? even? (range 5000))")
        result = seval(expr, env)
        assert result is True

    def test_all_large_list(self):
        """Test all? is stack-safe on a large list."""
        env = make_global_env()
        # Check if all elements are < 5000 in range 5000 (all should be)
        expr = read_one("(all? (lambda (x) (< x 5000)) (range 5000))")
        result = seval(expr, env)
        assert result is True

    def test_find_large_list(self):
        """Test find is stack-safe on a large list."""
        env = make_global_env()
        # Find the first element > 4999 in range 5000 (should not find any)
        expr = read_one("(find (lambda (x) (> x 4999)) (range 5000))")
        result = seval(expr, env)
        assert result is False

    def test_partition_large_list(self):
        """Test partition is stack-safe on a large list."""
        env = make_global_env()
        # Partition range 5000 into evens and odds, count the evens
        expr = read_one("(length (car (partition even? (range 5000))))")
        result = seval(expr, env)
        assert result == 2500
