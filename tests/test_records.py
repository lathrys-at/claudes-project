"""Tests for define-record macro."""
import pytest
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList


class TestDefineRecord:
    """Test define-record macro for user-defined record types."""

    def test_basic_point_creation_and_access(self):
        """Test basic record creation and field access."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (define p (make-point 3 4))
        (list (point-x p) (point-y p))
        """
        result = eval_source(code, env)
        assert result == PebbleList((3, 4))

    def test_point_predicate_true_for_own_type(self):
        """Test that predicate returns true for records of the correct type."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (define p (make-point 3 4))
        (point? p)
        """
        result = eval_source(code, env)
        assert result is True

    def test_point_predicate_false_for_number(self):
        """Test that predicate returns false for numbers."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (point? 5)
        """
        result = eval_source(code, env)
        assert result is False

    def test_point_predicate_false_for_string(self):
        """Test that predicate returns false for strings."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (point? "hello")
        """
        result = eval_source(code, env)
        assert result is False

    def test_point_predicate_false_for_plain_list(self):
        """Test that predicate returns false for plain lists."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (point? (list 1 2 3))
        """
        result = eval_source(code, env)
        assert result is False

    def test_point_predicate_false_for_plain_vector(self):
        """Test that predicate returns false for plain vectors."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (point? (vector 1 2))
        """
        result = eval_source(code, env)
        assert result is False

    def test_unforgeable_list_lookalike(self):
        """Test that a hand-crafted list resembling a record is NOT recognized as a record."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (point? (list (quote point) 3 4))
        """
        result = eval_source(code, env)
        assert result is False

    def test_unforgeable_vector_lookalike(self):
        """Test that a hand-crafted vector resembling a record is NOT recognized as a record."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (point? (vector (quote point) 3 4))
        """
        result = eval_source(code, env)
        assert result is False

    def test_two_record_types_are_distinct(self):
        """Test that two different record types are fully distinguished."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (define-record circle (radius))
        (define p (make-point 3 4))
        (define c (make-circle 10))
        (list (point? p) (point? c) (circle? p) (circle? c))
        """
        result = eval_source(code, env)
        assert result == PebbleList((True, False, False, True))

    def test_circle_predicate_and_accessor(self):
        """Test circle record type with single field."""
        env = make_global_env()
        code = """
        (define-record circle (radius))
        (define c (make-circle 10))
        (circle? c)
        (circle-radius c)
        """
        result = eval_source(code, env)
        assert result == 10

    def test_accessor_on_wrong_type_raises_error(self):
        """Test that accessing a field on wrong type raises EvalError."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (define-record circle (radius))
        (define c (make-circle 10))
        (point-x c)
        """
        with pytest.raises(Exception):  # EvalError
            eval_source(code, env)

    def test_accessor_on_non_record_raises_error(self):
        """Test that accessing a field on a non-record raises EvalError."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (point-x 5)
        """
        with pytest.raises(Exception):  # EvalError
            eval_source(code, env)

    def test_constructor_arity_too_few_raises_error(self):
        """Test that constructor with too few args raises EvalError."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (make-point 1)
        """
        with pytest.raises(Exception):  # EvalError
            eval_source(code, env)

    def test_constructor_arity_too_many_raises_error(self):
        """Test that constructor with too many args raises EvalError."""
        env = make_global_env()
        code = """
        (define-record point (x y))
        (make-point 1 2 3)
        """
        with pytest.raises(Exception):  # EvalError
            eval_source(code, env)

    def test_record_equality_same_values(self):
        """Test that two records of same type with same fields are equal."""
        env = make_global_env()
        eval_source("(define-record point (x y))", env)
        code = "(= (make-point 3 4) (make-point 3 4))"
        result = eval_source(code, env)
        assert result is True

    def test_record_inequality_different_values(self):
        """Test that two records with different field values are not equal."""
        env = make_global_env()
        eval_source("(define-record point (x y))", env)
        code = """
        (= (make-point 3 4) (make-point 3 5))
        """
        result = eval_source(code, env)
        assert result is False

    def test_record_inequality_different_types(self):
        """Test that records of different types are not equal."""
        env = make_global_env()
        eval_source("""
        (define-record point (x y))
        (define-record circle (radius))
        """, env)
        code = """
        (= (make-point 3 4) (make-circle 3))
        """
        result = eval_source(code, env)
        assert result is False

    def test_record_in_function(self):
        """Test using a record in a function."""
        env = make_global_env()
        eval_source("""
        (define-record point (x y))
        (define (dist-sq p)
          (+ (* (point-x p) (point-x p)) (* (point-y p) (point-y p))))
        """, env)
        code = "(dist-sq (make-point 3 4))"
        result = eval_source(code, env)
        assert result == 25

    def test_record_as_list_element(self):
        """Test storing a record in a list and retrieving it."""
        env = make_global_env()
        eval_source("(define-record point (x y))", env)
        code = """
        (define points (list (make-point 1 2) (make-point 3 4)))
        (point-y (car points))
        """
        result = eval_source(code, env)
        assert result == 2

    def test_define_record_returns_name(self):
        """Test that define-record returns the record name symbol."""
        env = make_global_env()
        code = "(define-record point (x y))"
        result = eval_source(code, env)
        # The macro should return the name symbol
        assert str(result) == "point"

    def test_three_field_record(self):
        """Test a record with three fields."""
        env = make_global_env()
        eval_source("""
        (define-record rgb (red green blue))
        """, env)
        code = """
        (define c (make-rgb 255 128 64))
        (list (rgb-red c) (rgb-green c) (rgb-blue c))
        """
        result = eval_source(code, env)
        assert result == PebbleList((255, 128, 64))

    def test_record_with_nested_values(self):
        """Test a record holding other records."""
        env = make_global_env()
        eval_source("""
        (define-record point (x y))
        (define-record line (start end))
        """, env)
        code = """
        (define p1 (make-point 1 2))
        (define p2 (make-point 3 4))
        (define l (make-line p1 p2))
        (point-x (line-start l))
        """
        result = eval_source(code, env)
        assert result == 1

    def test_multiple_instances_are_distinct(self):
        """Test that multiple instances are distinct and independent."""
        env = make_global_env()
        eval_source("(define-record point (x y))", env)
        code = """
        (define p1 (make-point 1 2))
        (define p2 (make-point 1 2))
        (and (point? p1) (point? p2) (= p1 p2) (not (= p1 (make-point 1 3))))
        """
        result = eval_source(code, env)
        assert result is True
