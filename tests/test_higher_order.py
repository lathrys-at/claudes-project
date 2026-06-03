"""Tests for higher-order utility functions: scanl, tabulate, find-index"""

import pytest
from pebble.reader import read_one
from pebble.evaluator import make_global_env, seval, EvalError, eval_source
from pebble.types import PebbleList, NIL, Symbol


def test_scanl_with_addition():
    """Test scanl with addition operator."""
    env = make_global_env()
    expr = read_one("(scanl + 0 (list 1 2 3 4))")
    result = seval(expr, env)
    # Expected: (0 1 3 6 10)
    assert isinstance(result, PebbleList)
    values = list(result)
    assert values == [0, 1, 3, 6, 10]


def test_scanl_with_empty_list():
    """Test scanl with empty list."""
    env = make_global_env()
    expr = read_one("(scanl + 0 nil)")
    result = seval(expr, env)
    # Expected: (0)
    assert isinstance(result, PebbleList)
    assert len(result) == 1
    assert result[0] == 0


def test_scanl_with_multiplication():
    """Test scanl with multiplication operator."""
    env = make_global_env()
    expr = read_one("(scanl * 1 (list 1 2 3 4))")
    result = seval(expr, env)
    # Expected: (1 1 2 6 24)
    assert isinstance(result, PebbleList)
    values = list(result)
    assert values == [1, 1, 2, 6, 24]


def test_scanl_with_different_init():
    """Test scanl with a different initial value."""
    env = make_global_env()
    expr = read_one("(scanl + 10 (list 1 2 3))")
    result = seval(expr, env)
    # Expected: (10 11 13 16)
    assert isinstance(result, PebbleList)
    values = list(result)
    assert values == [10, 11, 13, 16]


def test_tabulate_squares():
    """Test tabulate with square function."""
    env = make_global_env()
    expr = read_one("(tabulate (lambda (i) (* i i)) 5)")
    result = seval(expr, env)
    # Expected: (0 1 4 9 16)
    assert isinstance(result, PebbleList)
    values = list(result)
    assert values == [0, 1, 4, 9, 16]


def test_tabulate_zero_count():
    """Test tabulate with zero count."""
    env = make_global_env()
    expr = read_one("(tabulate (lambda (i) i) 0)")
    result = seval(expr, env)
    # Expected: empty list (nil)
    assert isinstance(result, PebbleList)
    assert len(result) == 0


def test_tabulate_identity():
    """Test tabulate with identity and count 3."""
    env = make_global_env()
    expr = read_one("(tabulate (lambda (i) (+ i 1)) 3)")
    result = seval(expr, env)
    # Expected: (1 2 3)
    assert isinstance(result, PebbleList)
    values = list(result)
    assert values == [1, 2, 3]


def test_tabulate_double():
    """Test tabulate with doubling function."""
    env = make_global_env()
    expr = read_one("(tabulate (lambda (i) (* i 2)) 4)")
    result = seval(expr, env)
    # Expected: (0 2 4 6)
    assert isinstance(result, PebbleList)
    values = list(result)
    assert values == [0, 2, 4, 6]


def test_tabulate_negative_count():
    """Test tabulate with negative count raises EvalError."""
    env = make_global_env()
    expr = read_one("(tabulate (lambda (i) i) -1)")
    with pytest.raises(EvalError):
        seval(expr, env)


def test_find_index_found():
    """Test find-index when element is found."""
    env = make_global_env()
    expr = read_one("(find-index even? (list 1 3 4 5))")
    result = seval(expr, env)
    # Expected: 2 (4 is at index 2)
    assert result == 2


def test_find_index_not_found():
    """Test find-index when no element satisfies predicate."""
    env = make_global_env()
    expr = read_one("(find-index even? (list 1 3 5))")
    result = seval(expr, env)
    # Expected: -1
    assert result == -1


def test_find_index_empty_list():
    """Test find-index with empty list."""
    env = make_global_env()
    expr = read_one("(find-index even? nil)")
    result = seval(expr, env)
    # Expected: -1
    assert result == -1


def test_find_index_with_lambda():
    """Test find-index with custom lambda predicate."""
    env = make_global_env()
    expr = read_one("(find-index (lambda (x) (> x 3)) (list 1 2 3 4 5))")
    result = seval(expr, env)
    # Expected: 3 (4 is at index 3)
    assert result == 3


def test_find_index_equality():
    """Test find-index with equality predicate."""
    env = make_global_env()
    expr = read_one("(find-index (lambda (x) (= x 0)) (list 5 0 5))")
    result = seval(expr, env)
    # Expected: 1
    assert result == 1


def test_scanl_large_list_stack_safety():
    """Test scanl with large list (3000 elements) for stack safety."""
    env = make_global_env()
    expr = read_one("(scanl + 0 (range 3000))")
    result = seval(expr, env)
    # Expected: list of length 3001
    assert isinstance(result, PebbleList)
    assert len(result) == 3001
    # First element should be 0 (init)
    assert result[0] == 0
    # Last element should be the sum of 0..2999
    expected_last = sum(range(3000))
    assert result[-1] == expected_last


def test_find_index_large_list_stack_safety():
    """Test find-index with large list (3000 elements) for stack safety."""
    env = make_global_env()
    expr = read_one("(find-index (lambda (x) (= x 2999)) (range 3000))")
    result = seval(expr, env)
    # Expected: 2999
    assert result == 2999


def test_scanl_length():
    """Test that scanl result has correct length."""
    env = make_global_env()
    expr = read_one("(length (scanl + 0 (list 1 2 3 4)))")
    result = seval(expr, env)
    # Input list has length 4, scanl should return length 5
    assert result == 5


def test_scanl_empty_length():
    """Test that scanl on empty list returns length 1."""
    env = make_global_env()
    expr = read_one("(length (scanl + 0 nil))")
    result = seval(expr, env)
    # Input is empty, scanl should return (init), length 1
    assert result == 1


def test_tabulate_non_integer():
    """Test that tabulate with non-integer raises EvalError."""
    env = make_global_env()
    expr = read_one("(tabulate (lambda (i) i) 1.5)")
    with pytest.raises(EvalError):
        seval(expr, env)
