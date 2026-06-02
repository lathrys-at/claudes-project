"""Tests for functional combinators: partial, flip, complement."""

import pytest
from pebble.evaluator import make_global_env, eval_source


def eval_pebble(code):
    """Evaluate Pebble code and return the result."""
    env = make_global_env()
    return eval_source(code, env)


def test_partial_with_single_fixed_arg():
    """Test partial with a single fixed argument."""
    result = eval_pebble("((partial + 10) 5)")
    assert result == 15


def test_partial_with_multiple_fixed_args():
    """Test partial with multiple fixed arguments."""
    result = eval_pebble("((partial + 1 2) 3 4)")
    assert result == 10


def test_partial_with_no_fixed_args():
    """Test partial with no fixed arguments (just wraps the function)."""
    result = eval_pebble("((partial +) 2 3)")
    assert result == 5


def test_partial_with_cons():
    """Test partial used with cons, building a list."""
    result = eval_pebble("((partial cons 1) (list 2 3))")
    # Result should be the list (1 2 3)
    assert list(result) == [1, 2, 3]


def test_partial_with_user_defined_function():
    """Test partial with a user-defined function."""
    code = """
    (define (add3 a b c) (+ a b c))
    ((partial add3 10) 20 30)
    """
    result = eval_pebble(code)
    assert result == 60


def test_partial_multiple_fixed_args_with_multiple_later_args():
    """Test partial capturing multiple fixed args and combining with multiple later args."""
    code = """
    (define (sum4 a b c d) (+ a b c d))
    ((partial sum4 1 2) 3 4)
    """
    result = eval_pebble(code)
    assert result == 10


def test_flip_on_subtraction():
    """Test flip swaps arguments on non-commutative operations."""
    result = eval_pebble("((flip -) 3 10)")
    # (flip -) swaps args, so ((flip -) 3 10) = (- 10 3) = 7
    assert result == 7


def test_flip_on_cons():
    """Test flip on cons."""
    result = eval_pebble("((flip cons) (list 2 3) 1)")
    # (flip cons) swaps args, so ((flip cons) (list 2 3) 1) = (cons 1 (list 2 3))
    assert list(result) == [1, 2, 3]


def test_complement_on_single_predicate():
    """Test complement on single-argument predicate (even?)."""
    result = eval_pebble("((complement even?) 3)")
    assert result is True


def test_complement_on_single_predicate_true_case():
    """Test complement on single-argument predicate when pred would be true."""
    result = eval_pebble("((complement even?) 4)")
    assert result is False


def test_complement_on_null():
    """Test complement on null? predicate."""
    result = eval_pebble("((complement null?) (list 1))")
    assert result is True


def test_complement_on_empty_list():
    """Test complement on null? predicate with empty list."""
    result = eval_pebble("((complement null?) nil)")
    assert result is False


def test_complement_on_multi_arg_predicate():
    """Test complement on a multi-argument predicate (= equals)."""
    result = eval_pebble("((complement =) 1 2)")
    assert result is True


def test_complement_on_multi_arg_predicate_equal_args():
    """Test complement on equals when arguments are equal."""
    result = eval_pebble("((complement =) 2 2)")
    assert result is False


def test_compose_with_partial():
    """Test that compose works alongside partial."""
    code = """
    ((compose (partial + 1) (partial * 2)) 5)
    """
    result = eval_pebble(code)
    # (partial * 2) applies * 2, so (partial * 2) 5 = (* 2 5) = 10
    # (partial + 1) applies + 1, so (partial + 1) 10 = (+ 1 10) = 11
    assert result == 11


def test_partial_and_flip_combined():
    """Test partial and flip used together."""
    code = """
    ((partial (flip cons) (list 2 3)) 1)
    """
    result = eval_pebble(code)
    # (flip cons) swaps arguments
    # (partial (flip cons) (list 2 3)) returns a function that when called with more args
    # calls (flip cons) with (list 2 3) followed by more args
    # So ((partial (flip cons) (list 2 3)) 1) = ((flip cons) (list 2 3) 1) = (cons 1 (list 2 3))
    assert list(result) == [1, 2, 3]


def test_complement_with_lambda():
    """Test complement works with user-defined predicates."""
    code = """
    (define (positive? n) (> n 0))
    ((complement positive?) -5)
    """
    result = eval_pebble(code)
    assert result is True


def test_complement_with_lambda_false_case():
    """Test complement with user-defined predicate when original is true."""
    code = """
    (define (positive? n) (> n 0))
    ((complement positive?) 5)
    """
    result = eval_pebble(code)
    assert result is False


def test_partial_preserves_function_semantics():
    """Test that partial preserves the original function's behavior."""
    code = """
    (define (multiply a b) (* a b))
    (= ((partial multiply 3) 4) (multiply 3 4))
    """
    result = eval_pebble(code)
    assert result is True


def test_partial_with_foldl():
    """Test partial used with higher-order functions like foldl."""
    code = """
    (foldl (partial + 10) 0 (list 1 2 3))
    """
    result = eval_pebble(code)
    # foldl starts with acc=0
    # ((partial + 10) 0 1) = (+ 10 0 1) - but wait, foldl calls (f acc elem)
    # So ((partial + 10) 0 1) = (+ 10 0) then on next element ((partial + 10) 10 2) = (+ 10 10) = 20
    # Actually, let's trace: foldl (partial + 10) 0 (list 1 2 3)
    # Step 1: ((partial + 10) 0 1) = (+ 10 0 1) - foldl passes (acc elem) = (0 1) to the function
    # Wait, (partial + 10) when called with (0 1) args means (apply + (append (list 10) (list 0 1)))
    # = (+ 10 0 1) = 11
    # Step 2: ((partial + 10) 11 2) = (+ 10 11 2) = 23
    # Step 3: ((partial + 10) 23 3) = (+ 10 23 3) = 36
    assert result == 36


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
