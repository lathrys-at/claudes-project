"""Test suite for chunk, interleave, and enumerate list utilities."""
import pytest
from pebble.evaluator import make_global_env
from pebble.types import PebbleList, Symbol, NIL
from pebble.reader import read_one
from pebble.evaluator import seval


def make_env():
    """Create a fresh global environment for each test."""
    return make_global_env()


def eval_pebble(code, env):
    """Evaluate Pebble source code in the given environment."""
    expr = read_one(code)
    return seval(expr, env)


class TestChunk:
    """Tests for the chunk function."""

    def test_chunk_basic_even(self):
        """chunk with size 2, length divisible by 2."""
        env = make_env()
        result = eval_pebble("(chunk (list 1 2 3 4 5) 2)", env)
        # Expected: ((1 2) (3 4) (5))
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        chunk1 = result[0]
        chunk2 = result[1]
        chunk3 = result[2]
        assert chunk1 == PebbleList([1, 2])
        assert chunk2 == PebbleList([3, 4])
        assert chunk3 == PebbleList([5])

    def test_chunk_exact_division(self):
        """chunk where length is exactly divisible."""
        env = make_env()
        result = eval_pebble("(chunk (list 1 2 3 4) 2)", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 2
        chunk1 = result[0]
        chunk2 = result[1]
        assert chunk1 == PebbleList([1, 2])
        assert chunk2 == PebbleList([3, 4])

    def test_chunk_size_one(self):
        """chunk with size 1."""
        env = make_env()
        result = eval_pebble("(chunk (list 1 2 3) 1)", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == PebbleList([1])
        assert result[1] == PebbleList([2])
        assert result[2] == PebbleList([3])

    def test_chunk_larger_than_list(self):
        """chunk with size larger than the list."""
        env = make_env()
        result = eval_pebble("(chunk (list 1 2 3) 5)", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 1
        chunk1 = result[0]
        assert chunk1 == PebbleList([1, 2, 3])

    def test_chunk_empty_list(self):
        """chunk with empty list."""
        env = make_env()
        result = eval_pebble("(chunk nil 3)", env)
        assert result == NIL


class TestInterleave:
    """Tests for the interleave function."""

    def test_interleave_equal_length(self):
        """interleave two lists of equal length."""
        env = make_env()
        result = eval_pebble("(interleave (list 1 2 3) (list 'a 'b 'c))", env)
        assert isinstance(result, PebbleList)
        expected = PebbleList([1, Symbol('a'), 2, Symbol('b'), 3, Symbol('c')])
        assert result == expected

    def test_interleave_first_shorter(self):
        """interleave where first list is shorter."""
        env = make_env()
        result = eval_pebble("(interleave (list 1 2 3) (list 'a))", env)
        assert isinstance(result, PebbleList)
        expected = PebbleList([1, Symbol('a')])
        assert result == expected

    def test_interleave_second_shorter(self):
        """interleave where second list is shorter."""
        env = make_env()
        result = eval_pebble("(interleave (list 1) (list 'a 'b 'c))", env)
        assert isinstance(result, PebbleList)
        expected = PebbleList([1, Symbol('a')])
        assert result == expected

    def test_interleave_first_empty(self):
        """interleave with first list empty."""
        env = make_env()
        result = eval_pebble("(interleave nil (list 1 2))", env)
        assert result == NIL

    def test_interleave_second_empty(self):
        """interleave with second list empty."""
        env = make_env()
        result = eval_pebble("(interleave (list 1 2) nil)", env)
        assert result == NIL


class TestEnumerate:
    """Tests for the enumerate function."""

    def test_enumerate_basic(self):
        """enumerate a basic list."""
        env = make_env()
        result = eval_pebble("(enumerate (list 'a 'b 'c))", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        # First pair should be (0 a)
        pair1 = result[0]
        assert pair1 == PebbleList([0, Symbol('a')])
        # Second pair should be (1 b)
        pair2 = result[1]
        assert pair2 == PebbleList([1, Symbol('b')])
        # Third pair should be (2 c)
        pair3 = result[2]
        assert pair3 == PebbleList([2, Symbol('c')])

    def test_enumerate_empty(self):
        """enumerate an empty list."""
        env = make_env()
        result = eval_pebble("(enumerate nil)", env)
        assert result == NIL

    def test_enumerate_single(self):
        """enumerate a single-element list."""
        env = make_env()
        result = eval_pebble("(enumerate (list 10))", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 1
        pair1 = result[0]
        assert pair1 == PebbleList([0, 10])


class TestStackSafety:
    """Tests for stack-safety with large lists."""

    def test_chunk_stack_safety(self):
        """chunk should be stack-safe with 2000-element list."""
        env = make_env()
        # (length (chunk (range 2000) 10)) should be 200
        result = eval_pebble("(length (chunk (range 2000) 10))", env)
        assert result == 200

    def test_enumerate_stack_safety(self):
        """enumerate should be stack-safe with 2000-element list."""
        env = make_env()
        # (length (enumerate (range 2000))) should be 2000
        result = eval_pebble("(length (enumerate (range 2000)))", env)
        assert result == 2000
