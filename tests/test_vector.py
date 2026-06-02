"""Tests for mutable vector data type."""
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


def test_vector_construction():
    """Test basic vector construction with (vector ...)."""
    result = eval_expr("(vector 1 2 3)")
    assert isinstance(result, PebbleVector)
    assert len(result) == 3
    assert result[0] == 1
    assert result[1] == 2
    assert result[2] == 3


def test_empty_vector():
    """Test empty vector construction."""
    result = eval_expr("(vector)")
    assert isinstance(result, PebbleVector)
    assert len(result) == 0


def test_vector_length():
    """Test vector-length builtin."""
    result = eval_expr("(vector-length (vector 1 2 3))")
    assert result == 3

    result = eval_expr("(vector-length (vector))")
    assert result == 0


def test_make_vector_default_fill():
    """Test make-vector with default nil fill."""
    result = eval_expr("(make-vector 3)")
    assert isinstance(result, PebbleVector)
    assert len(result) == 3
    assert result[0] == NIL
    assert result[1] == NIL
    assert result[2] == NIL


def test_make_vector_custom_fill():
    """Test make-vector with explicit fill value."""
    result = eval_expr("(make-vector 3 42)")
    assert isinstance(result, PebbleVector)
    assert len(result) == 3
    assert result[0] == 42
    assert result[1] == 42
    assert result[2] == 42


def test_make_vector_empty():
    """Test make-vector with n=0."""
    result = eval_expr("(make-vector 0)")
    assert isinstance(result, PebbleVector)
    assert len(result) == 0


def test_make_vector_negative_length():
    """Test make-vector with negative length raises error."""
    with pytest.raises(EvalError):
        eval_expr("(make-vector -1)")


def test_make_vector_non_integer_length():
    """Test make-vector with non-integer length raises error."""
    with pytest.raises(EvalError):
        eval_expr("(make-vector 3.5)")


def test_vector_predicate():
    """Test vector? predicate."""
    assert eval_expr("(vector? (vector 1 2))") is True
    assert eval_expr("(vector? (vector))") is True
    assert eval_expr("(vector? (list 1 2))") is False
    assert eval_expr("(vector? (make-hash))") is False
    assert eval_expr("(vector? 42)") is False


def test_vector_ref():
    """Test vector-ref builtin."""
    result = eval_expr("(vector-ref (vector 10 20 30) 0)")
    assert result == 10

    result = eval_expr("(vector-ref (vector 10 20 30) 1)")
    assert result == 20

    result = eval_expr("(vector-ref (vector 10 20 30) 2)")
    assert result == 30


def test_vector_ref_out_of_range():
    """Test vector-ref with out of range index."""
    with pytest.raises(EvalError):
        eval_expr("(vector-ref (vector 1 2) 5)")


def test_vector_ref_negative_index():
    """Test vector-ref with negative index."""
    with pytest.raises(EvalError):
        eval_expr("(vector-ref (vector 1 2) -1)")


def test_vector_ref_non_integer_index():
    """Test vector-ref with non-integer index."""
    with pytest.raises(EvalError):
        eval_expr("(vector-ref (vector 1 2) 1.5)")


def test_vector_ref_non_vector():
    """Test vector-ref with non-vector first arg."""
    with pytest.raises(EvalError):
        eval_expr("(vector-ref (list 1 2) 0)")


def test_vector_set_mutation():
    """Test vector-set! mutates the vector in place."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-set! v 1 99)
      (vector-ref v 1))
    """)
    assert result == 99


def test_vector_set_returns_nil():
    """Test vector-set! returns nil."""
    result = eval_expr("(vector-set! (vector 1 2 3) 0 5)")
    assert result == NIL


def test_vector_mutation_aliasing():
    """Test that vector mutations are visible through all references."""
    result = eval_expr("""
    (let* ((a (vector 1 2 3))
           (b a))
      (vector-set! a 0 99)
      (vector-ref b 0))
    """)
    assert result == 99


def test_vector_set_out_of_range():
    """Test vector-set! with out of range index."""
    with pytest.raises(EvalError):
        eval_expr("(vector-set! (vector 1 2) 5 99)")


def test_vector_set_non_vector():
    """Test vector-set! with non-vector first arg."""
    with pytest.raises(EvalError):
        eval_expr("(vector-set! (list 1 2) 0 99)")


def test_vector_push():
    """Test vector-push! appends to vector."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-push! v 4)
      (vector-length v))
    """)
    assert result == 4


def test_vector_push_returns_nil():
    """Test vector-push! returns nil."""
    result = eval_expr("(vector-push! (vector) 1)")
    assert result == NIL


def test_vector_push_element_added():
    """Test vector-push! adds element at end."""
    result = eval_expr("""
    (let ((v (vector 1 2)))
      (vector-push! v 3)
      (vector-ref v 2))
    """)
    assert result == 3


def test_vector_to_list():
    """Test vector->list conversion."""
    result = eval_expr("(vector->list (vector 1 2 3))")
    assert isinstance(result, PebbleList)
    assert len(result) == 3
    assert result[0] == 1
    assert result[1] == 2
    assert result[2] == 3


def test_vector_to_list_empty():
    """Test vector->list with empty vector."""
    result = eval_expr("(vector->list (vector))")
    assert isinstance(result, PebbleList)
    assert len(result) == 0


def test_list_to_vector():
    """Test list->vector conversion."""
    result = eval_expr("(list->vector (list 1 2 3))")
    assert isinstance(result, PebbleVector)
    assert len(result) == 3
    assert result[0] == 1
    assert result[1] == 2
    assert result[2] == 3


def test_list_to_vector_empty():
    """Test list->vector with empty list."""
    result = eval_expr("(list->vector nil)")
    assert isinstance(result, PebbleVector)
    assert len(result) == 0


def test_vector_list_roundtrip():
    """Test vector->list->vector roundtrip."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (= v (list->vector (vector->list v))))
    """)
    assert result is True


def test_vector_equality():
    """Test that vectors with same elements are equal."""
    result = eval_expr("(= (vector 1 2 3) (vector 1 2 3))")
    assert result is True


def test_vector_inequality():
    """Test that vectors with different elements are not equal."""
    result = eval_expr("(= (vector 1 2 3) (vector 1 2 4))")
    assert result is False


def test_vector_equality_after_mutation():
    """Test that equal vectors become unequal after mutation."""
    result = eval_expr("""
    (let* ((a (vector 1 2 3))
           (b (vector 1 2 3)))
      (vector-set! a 0 99)
      (= a b))
    """)
    assert result is False


def test_vector_truthy():
    """Test that vectors are truthy."""
    result = eval_expr("(if (vector 1 2 3) \"yes\" \"no\")")
    assert result == "yes"


def test_empty_vector_truthy():
    """Test that empty vectors are also truthy."""
    result = eval_expr("(if (vector) \"yes\" \"no\")")
    assert result == "yes"


def test_vector_repr_empty():
    """Test pebble_repr for empty vector."""
    v = PebbleVector()
    assert pebble_repr(v) == "#()"


def test_vector_repr_non_empty():
    """Test pebble_repr for non-empty vector."""
    v = PebbleVector([1, 2, 3])
    assert pebble_repr(v) == "#(1 2 3)"


def test_vector_repr_with_strings():
    """Test pebble_repr for vector with strings."""
    result = eval_expr('(vector "hello" "world")')
    assert pebble_repr(result) == '#("hello" "world")'


def test_vector_repr_nested():
    """Test pebble_repr for vector containing vectors."""
    result = eval_expr("(vector (vector 1 2) (vector 3 4))")
    assert pebble_repr(result) == "#(#(1 2) #(3 4))"


def test_vector_with_nil():
    """Test vectors containing nil."""
    result = eval_expr("(vector 1 nil 3)")
    assert isinstance(result, PebbleVector)
    assert result[1] == NIL
    assert pebble_repr(result) == "#(1 nil 3)"


def test_complex_vector_mutations():
    """Test a more complex mutation scenario."""
    result = eval_expr("""
    (let ((v (vector 10 20 30)))
      (vector-push! v 40)
      (vector-set! v 0 100)
      (vector-length v))
    """)
    assert result == 4


def test_vector_with_different_types():
    """Test vectors containing mixed types."""
    result = eval_expr('(vector 1 "hello" true nil (list 5 6))')
    assert isinstance(result, PebbleVector)
    assert result[0] == 1
    assert result[1] == "hello"
    assert result[2] is True
    assert result[3] == NIL
    assert isinstance(result[4], PebbleList)


# ===== VECTOR-MAP TESTS =====

def test_vector_map_basic():
    """Test vector-map with a simple function."""
    result = eval_expr("(vector->list (vector-map (lambda (x) (* x x)) (vector 1 2 3)))")
    assert isinstance(result, PebbleList)
    assert len(result) == 3
    assert result[0] == 1
    assert result[1] == 4
    assert result[2] == 9


def test_vector_map_original_unchanged():
    """Test that vector-map doesn't modify the original vector."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-map (lambda (x) (* x x)) v)
      (vector->list v))
    """)
    assert result[0] == 1
    assert result[1] == 2
    assert result[2] == 3


def test_vector_map_empty():
    """Test vector-map with empty vector."""
    result = eval_expr("(vector->list (vector-map (lambda (x) x) (vector)))")
    assert len(result) == 0


def test_vector_map_non_vector_error():
    """Test that vector-map on non-vector raises an error."""
    with pytest.raises(EvalError):
        eval_expr("(vector-map (lambda (x) x) (list 1 2 3))")


# ===== VECTOR-FOR-EACH TESTS =====

def test_vector_for_each_basic():
    """Test vector-for-each with side effects."""
    result = eval_expr("""
    (let ((sum 0))
      (vector-for-each (lambda (x) (set! sum (+ sum x))) (vector 1 2 3))
      sum)
    """)
    assert result == 6


def test_vector_for_each_returns_nil():
    """Test that vector-for-each returns nil."""
    result = eval_expr("(vector-for-each (lambda (x) x) (vector 1 2 3))")
    assert result == NIL


def test_vector_for_each_empty():
    """Test vector-for-each with empty vector."""
    result = eval_expr("""
    (let ((called 0))
      (vector-for-each (lambda (x) (set! called (+ called 1))) (vector))
      called)
    """)
    assert result == 0


def test_vector_for_each_non_vector_error():
    """Test that vector-for-each on non-vector raises an error."""
    with pytest.raises(EvalError):
        eval_expr("(vector-for-each (lambda (x) x) (list 1 2 3))")


# ===== VECTOR-COPY TESTS =====

def test_vector_copy_basic():
    """Test that vector-copy creates a new vector with same elements."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (= v (vector-copy v)))
    """)
    assert result is True


def test_vector_copy_independence():
    """Test that vector-copy produces an independent copy."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (let ((c (vector-copy v)))
        (vector-set! c 0 99)
        (vector-ref v 0)))
    """)
    assert result == 1


def test_vector_copy_original_independent():
    """Test that mutating original doesn't affect the copy."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (let ((c (vector-copy v)))
        (vector-set! v 1 99)
        (vector-ref c 1)))
    """)
    assert result == 2


def test_vector_copy_empty():
    """Test vector-copy with empty vector."""
    result = eval_expr("(vector->list (vector-copy (vector)))")
    assert len(result) == 0


def test_vector_copy_non_vector_error():
    """Test that vector-copy on non-vector raises an error."""
    with pytest.raises(EvalError):
        eval_expr("(vector-copy (list 1 2 3))")


# ===== VECTOR-FILL! TESTS =====

def test_vector_fill_basic():
    """Test vector-fill! fills all elements."""
    result = eval_expr("""
    (let ((v (make-vector 3)))
      (vector-fill! v 42)
      (vector->list v))
    """)
    assert result[0] == 42
    assert result[1] == 42
    assert result[2] == 42


def test_vector_fill_returns_nil():
    """Test that vector-fill! returns nil."""
    result = eval_expr("(vector-fill! (vector 1 2 3) 0)")
    assert result == NIL


def test_vector_fill_aliasing():
    """Test that vector-fill! mutation is visible through aliases."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (let ((a v))
        (vector-fill! a 99)
        (vector-ref v 0)))
    """)
    assert result == 99


def test_vector_fill_length_unchanged():
    """Test that vector-fill! preserves vector length."""
    result = eval_expr("""
    (let ((v (vector 1 2 3)))
      (vector-fill! v 0)
      (vector-length v))
    """)
    assert result == 3


def test_vector_fill_empty():
    """Test vector-fill! with empty vector."""
    result = eval_expr("""
    (let ((v (vector)))
      (vector-fill! v 42)
      (vector-length v))
    """)
    assert result == 0


def test_vector_fill_non_vector_error():
    """Test that vector-fill! on non-vector raises an error."""
    with pytest.raises(EvalError):
        eval_expr("(vector-fill! (list 1 2 3) 0)")
