"""Tests for vector stack operations (vector-pop! and vector-last)."""
import pytest
from pebble.evaluator import make_global_env, seval, EvalError
from pebble.reader import read_one
from pebble.types import PebbleVector, NIL, PebbleList
from pebble.printer import pebble_repr


def eval_expr(expr_str):
    """Evaluate a Pebble expression string and return the result."""
    env = make_global_env()
    parsed = read_one(expr_str)
    return seval(parsed, env)


# ===== VECTOR-LAST TESTS =====

def test_vector_last_basic():
    """Test vector-last returns the last element."""
    result = eval_expr("(vector-last (vector 1 2 3))")
    assert result == 3


def test_vector_last_single_element():
    """Test vector-last with single element vector."""
    result = eval_expr("(vector-last (vector 42))")
    assert result == 42


def test_vector_last_different_types():
    """Test vector-last with different element types."""
    result = eval_expr('(vector-last (vector "hello" "world"))')
    assert result == "world"


def test_vector_last_does_not_modify():
    """Test that vector-last does not modify the vector."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-last v)
      (vector-length v))
    """)
    assert result == 3


def test_vector_last_does_not_modify_elements():
    """Test that vector-last does not modify the vector's elements."""
    result = eval_expr("""
    (let ((v (vector 10 20 30)))
      (vector-last v)
      (vector-ref v 2))
    """)
    assert result == 30


def test_vector_last_empty_error():
    """Test that vector-last on empty vector raises EvalError."""
    with pytest.raises(EvalError) as exc_info:
        eval_expr("(vector-last (vector))")
    assert "empty" in str(exc_info.value).lower()


def test_vector_last_non_vector_error():
    """Test that vector-last on non-vector raises EvalError."""
    with pytest.raises(EvalError) as exc_info:
        eval_expr("(vector-last (list 1 2 3))")
    assert "vector" in str(exc_info.value).lower()


def test_vector_last_non_vector_number_error():
    """Test that vector-last on a number raises EvalError."""
    with pytest.raises(EvalError):
        eval_expr("(vector-last 42)")


# ===== VECTOR-POP! TESTS =====

def test_vector_pop_basic():
    """Test vector-pop! removes and returns the last element."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-pop! v))
    """)
    assert result == 3


def test_vector_pop_shrinks_vector():
    """Test that vector-pop! shrinks the vector length."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-pop! v)
      (vector-length v))
    """)
    assert result == 2


def test_vector_pop_multiple():
    """Test multiple vector-pop! operations."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-pop! v)
      (vector-pop! v)
      (vector-length v))
    """)
    assert result == 1


def test_vector_pop_single_element():
    """Test vector-pop! on single element vector."""
    result = eval_expr("""
    (let ((v (vector 42)))
      (vector-pop! v)
      (vector-length v))
    """)
    assert result == 0


def test_vector_pop_empty_error():
    """Test that vector-pop! on empty vector raises EvalError."""
    with pytest.raises(EvalError) as exc_info:
        eval_expr("(vector-pop! (vector))")
    assert "empty" in str(exc_info.value).lower()


def test_vector_pop_non_vector_error():
    """Test that vector-pop! on non-vector raises EvalError."""
    with pytest.raises(EvalError) as exc_info:
        eval_expr("(vector-pop! (list 1 2 3))")
    assert "vector" in str(exc_info.value).lower()


# ===== ALIASING / MUTATION VISIBILITY TESTS =====

def test_vector_pop_aliasing():
    """Test that vector-pop! mutation is visible through aliases."""
    result = eval_expr("""
    (let* ((a (vector 1 2 3))
           (b a))
      (vector-pop! a)
      (vector-length b))
    """)
    assert result == 2


def test_vector_pop_aliasing_elements():
    """Test that popped vector changes are visible through aliases."""
    result = eval_expr("""
    (let* ((a (vector 10 20 30))
           (b a))
      (vector-pop! a)
      (vector-last b))
    """)
    assert result == 20


def test_vector_pop_aliasing_multiple_pops():
    """Test multiple pops visible through alias."""
    result = eval_expr("""
    (let* ((a (vector 1 2 3 4 5))
           (b a))
      (vector-pop! a)
      (vector-pop! a)
      (vector-ref b 2))
    """)
    assert result == 3


# ===== STACK USAGE TESTS =====

def test_vector_stack_lifo():
    """Test LIFO behavior with vector as stack: push 1, 2, 3 then pop."""
    result = eval_expr("""
    (let ((v (vector)))
      (vector-push! v 1)
      (vector-push! v 2)
      (vector-push! v 3)
      (vector-pop! v))
    """)
    assert result == 3


def test_vector_stack_lifo_sequence():
    """Test complete LIFO sequence: push 1, 2, 3 then pop 3, 2."""
    result = eval_expr("""
    (let ((v (vector)))
      (vector-push! v 1)
      (vector-push! v 2)
      (vector-push! v 3)
      (let ((x (vector-pop! v)))
        (let ((y (vector-pop! v)))
          (list x y (vector-length v) (vector-last v)))))
    """)
    # result should be a list: (3 2 1 1)
    assert result[0] == 3
    assert result[1] == 2
    assert result[2] == 1
    assert result[3] == 1


def test_vector_stack_reverse_sequence():
    """Test using vector as stack to reverse a sequence."""
    result = eval_expr("""
    (let ((v (vector)))
      (vector-push! v 1)
      (vector-push! v 2)
      (vector-push! v 3)
      (let ((rev (list)))
        (let loop ()
          (if (> (vector-length v) 0)
            (begin
              (set! rev (cons (vector-pop! v) rev))
              (loop))))
        rev))
    """)
    # result should be (1 2 3) since we pushed 1, 2, 3 then popped in reverse (3, 2, 1)
    # and cons'd them back to an empty list, resulting in (1 2 3)
    assert result[0] == 1
    assert result[1] == 2
    assert result[2] == 3


def test_vector_as_stack_peek_and_pop():
    """Test peeking with vector-last then popping with vector-pop!."""
    result = eval_expr("""
    (let ((v (vector 10 20 30)))
      (let ((last (vector-last v)))
        (let ((popped (vector-pop! v)))
          (list last popped (vector-length v)))))
    """)
    assert result[0] == 30
    assert result[1] == 30
    assert result[2] == 2


# ===== INTEGRATION TESTS =====

def test_vector_stack_with_different_types():
    """Test vector as stack with mixed element types."""
    result = eval_expr("""
    (let ((v (vector)))
      (vector-push! v 1)
      (vector-push! v "hello")
      (vector-push! v true)
      (list (vector-pop! v) (vector-pop! v) (vector-pop! v)))
    """)
    assert result[0] is True
    assert result[1] == "hello"
    assert result[2] == 1


def test_vector_stack_push_after_pop():
    """Test pushing after popping."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-pop! v)
      (vector-push! v 99)
      (vector->list v))
    """)
    # Should be (1 2 99)
    assert result[0] == 1
    assert result[1] == 2
    assert result[2] == 99


def test_vector_empty_after_pop_all():
    """Test that vector becomes empty after popping all elements."""
    result = eval_expr("""
    (let ((v (vector 1 2)))
      (vector-pop! v)
      (vector-pop! v)
      (vector-length v))
    """)
    assert result == 0


def test_vector_last_after_modifications():
    """Test vector-last after various modifications."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-pop! v)
      (vector-last v))
    """)
    assert result == 2


def test_vector_stack_complex_scenario():
    """Test a complex stack scenario with multiple operations."""
    result = eval_expr("""
    (let ((v (vector)))
      (vector-push! v "first")
      (vector-push! v "second")
      (vector-push! v "third")
      (let ((x (vector-pop! v)))
        (vector-push! v "fourth")
        (list x (vector-length v) (vector-last v))))
    """)
    assert result[0] == "third"
    assert result[1] == 3
    assert result[2] == "fourth"


# ===== ERROR CASES =====

def test_vector_pop_and_last_on_same_empty_vector():
    """Test both vector-pop! and vector-last error on empty vector."""
    with pytest.raises(EvalError):
        eval_expr("(vector-pop! (vector))")

    with pytest.raises(EvalError):
        eval_expr("(vector-last (vector))")


def test_vector_pop_non_vector_hash():
    """Test vector-pop! on hash raises error."""
    with pytest.raises(EvalError):
        eval_expr("(vector-pop! (make-hash))")


def test_vector_last_non_vector_hash():
    """Test vector-last on hash raises error."""
    with pytest.raises(EvalError):
        eval_expr("(vector-last (make-hash))")
