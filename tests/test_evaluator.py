"""Tests for the Pebble evaluator."""
import pytest
from pebble.evaluator import (
    seval, make_global_env, eval_source, EvalError, Environment, Procedure, is_truthy
)
from pebble.reader import read_one, read
from pebble.types import Symbol, PebbleList, NIL


class TestIsTargetful:
    """Tests for the is_truthy function."""

    def test_false_is_falsy(self):
        assert is_truthy(False) is False

    def test_empty_list_is_falsy(self):
        assert is_truthy(NIL) is False

    def test_nil_is_falsy(self):
        assert is_truthy(NIL) is False

    def test_zero_is_truthy(self):
        assert is_truthy(0) is True

    def test_zero_float_is_truthy(self):
        assert is_truthy(0.0) is True

    def test_empty_string_is_truthy(self):
        assert is_truthy("") is True

    def test_true_is_truthy(self):
        assert is_truthy(True) is True

    def test_non_empty_list_is_truthy(self):
        lst = PebbleList([1, 2, 3])
        assert is_truthy(lst) is True

    def test_positive_int_is_truthy(self):
        assert is_truthy(42) is True

    def test_string_is_truthy(self):
        assert is_truthy("hello") is True


class TestEnvironment:
    """Tests for the Environment class."""

    def test_define_and_lookup(self):
        env = Environment()
        env.define("x", 42)
        assert env.lookup("x") == 42

    def test_lookup_undefined_raises_error(self):
        env = Environment()
        with pytest.raises(EvalError, match="undefined symbol"):
            env.lookup("x")

    def test_lookup_in_parent(self):
        parent = Environment()
        parent.define("x", 10)
        child = Environment(parent=parent)
        assert child.lookup("x") == 10

    def test_define_shadows_parent(self):
        parent = Environment()
        parent.define("x", 10)
        child = Environment(parent=parent)
        child.define("x", 20)
        assert child.lookup("x") == 20
        assert parent.lookup("x") == 10

    def test_set_existing_variable(self):
        env = Environment()
        env.define("x", 10)
        env.set("x", 20)
        assert env.lookup("x") == 20

    def test_set_in_parent_scope(self):
        parent = Environment()
        parent.define("x", 10)
        child = Environment(parent=parent)
        child.set("x", 20)
        assert parent.lookup("x") == 20

    def test_set_undefined_raises_error(self):
        env = Environment()
        with pytest.raises(EvalError, match="cannot set undefined symbol"):
            env.set("x", 20)


class TestSelfEvaluating:
    """Tests for self-evaluating atoms."""

    def test_integer(self):
        env = make_global_env()
        result = seval(42, env)
        assert result == 42

    def test_float(self):
        env = make_global_env()
        result = seval(3.14, env)
        assert result == 3.14

    def test_string(self):
        env = make_global_env()
        result = seval("hello", env)
        assert result == "hello"

    def test_boolean_true(self):
        env = make_global_env()
        result = seval(True, env)
        assert result is True

    def test_boolean_false(self):
        env = make_global_env()
        result = seval(False, env)
        assert result is False

    def test_empty_list(self):
        env = make_global_env()
        result = seval(NIL, env)
        assert result is NIL


class TestArithmetic:
    """Tests for arithmetic operations."""

    def test_addition(self):
        expr = read_one("(+ 1 2 3)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 6

    def test_addition_no_args(self):
        expr = read_one("(+)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 0

    def test_addition_single_arg(self):
        expr = read_one("(+ 5)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 5

    def test_subtraction(self):
        expr = read_one("(- 10 3 2)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 5

    def test_subtraction_single_arg(self):
        expr = read_one("(- 5)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == -5

    def test_multiplication(self):
        expr = read_one("(* 2 3 4)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 24

    def test_multiplication_no_args(self):
        expr = read_one("(*)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 1

    def test_division(self):
        expr = read_one("(/ 12 3 2)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 2.0

    def test_division_by_zero_raises_error(self):
        expr = read_one("(/ 1 0)")
        env = make_global_env()
        with pytest.raises(EvalError, match="division by zero"):
            seval(expr, env)

    def test_nested_arithmetic(self):
        expr = read_one("(+ 1 (* 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 7

    def test_complex_nested_arithmetic(self):
        expr = read_one("(* (+ 1 2) (- 10 5))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 15


class TestComparisons:
    """Tests for comparison operations."""

    def test_less_than_true(self):
        expr = read_one("(< 1 2 3)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_less_than_false(self):
        expr = read_one("(< 1 3 2)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_greater_than_true(self):
        expr = read_one("(> 3 2 1)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_greater_than_false(self):
        expr = read_one("(> 3 1 2)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_less_than_or_equal_true(self):
        expr = read_one("(<= 1 2 2)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_less_than_or_equal_false(self):
        expr = read_one("(<= 1 2 1)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_greater_than_or_equal_true(self):
        expr = read_one("(>= 3 2 2)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_greater_than_or_equal_false(self):
        expr = read_one("(>= 3 2 3)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_equality_true(self):
        expr = read_one("(= 2 2 2)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_equality_false(self):
        expr = read_one("(= 2 2 3)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_equality_strings(self):
        expr = read_one('(= "hello" "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True


class TestQuote:
    """Tests for the quote special form."""

    def test_quote_number(self):
        expr = read_one("(quote 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 42

    def test_quote_symbol(self):
        expr = read_one("(quote x)")
        env = make_global_env()
        result = seval(expr, env)
        assert isinstance(result, Symbol)
        assert str(result) == "x"

    def test_quote_list(self):
        expr = read_one("(quote (1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert isinstance(result, PebbleList)
        assert list(result) == [1, 2, 3]

    def test_quote_shorthand(self):
        # 'x should be parsed as (quote x)
        expr = read_one("'x")
        env = make_global_env()
        result = seval(expr, env)
        assert isinstance(result, Symbol)
        assert str(result) == "x"

    def test_quote_malformed_no_arg(self):
        expr = read_one("(quote)")
        env = make_global_env()
        with pytest.raises(EvalError, match="quote requires exactly 1 argument"):
            seval(expr, env)


class TestIf:
    """Tests for the if special form."""

    def test_if_true_branch(self):
        expr = read_one("(if true 10 20)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 10

    def test_if_false_branch(self):
        expr = read_one("(if false 10 20)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 20

    def test_if_no_else(self):
        expr = read_one("(if false 10)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is NIL

    def test_if_with_condition_expression(self):
        expr = read_one("(if (< 1 2) 100 200)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 100

    def test_if_truthy_zero(self):
        expr = read_one("(if 0 10 20)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 10

    def test_if_falsy_empty_list(self):
        expr = read_one("(if nil 10 20)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 20

    def test_if_truthy_empty_string_no(self):
        # Empty string is truthy, so it evaluates the then branch
        expr = read_one('(if "" 10 20)')
        env = make_global_env()
        result = seval(expr, env)
        assert result == 10

    def test_if_malformed_too_few_args(self):
        expr = read_one("(if true)")
        env = make_global_env()
        with pytest.raises(EvalError, match="if requires 2 or 3 arguments"):
            seval(expr, env)

    def test_if_malformed_too_many_args(self):
        expr = read_one("(if true 10 20 30)")
        env = make_global_env()
        with pytest.raises(EvalError, match="if requires 2 or 3 arguments"):
            seval(expr, env)


class TestDefine:
    """Tests for the define special form."""

    def test_define_and_use_variable(self):
        env = make_global_env()
        expr1 = read_one("(define x 10)")
        seval(expr1, env)
        expr2 = read_one("x")
        result = seval(expr2, env)
        assert result == 10

    def test_define_returns_symbol(self):
        env = make_global_env()
        expr = read_one("(define x 10)")
        result = seval(expr, env)
        assert isinstance(result, Symbol)
        assert str(result) == "x"

    def test_define_expression_value(self):
        env = make_global_env()
        expr = read_one("(define x (+ 2 3))")
        seval(expr, env)
        expr2 = read_one("x")
        result = seval(expr2, env)
        assert result == 5

    def test_define_malformed_no_args(self):
        env = make_global_env()
        expr = read_one("(define)")
        with pytest.raises(EvalError, match="define requires at least 1 argument"):
            seval(expr, env)

    def test_define_malformed_non_symbol_name(self):
        env = make_global_env()
        expr = read_one("(define 42 10)")
        with pytest.raises(EvalError, match="define: first argument must be a symbol"):
            seval(expr, env)


class TestSet:
    """Tests for the set! special form."""

    def test_set_updates_variable(self):
        env = make_global_env()
        seval(read_one("(define x 10)"), env)
        result = seval(read_one("(set! x 20)"), env)
        assert result == 20
        assert seval(read_one("x"), env) == 20

    def test_set_returns_value(self):
        env = make_global_env()
        seval(read_one("(define x 10)"), env)
        result = seval(read_one("(set! x 30)"), env)
        assert result == 30

    def test_set_undefined_raises_error(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="cannot set undefined symbol"):
            seval(read_one("(set! x 20)"), env)

    def test_set_malformed_no_args(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="set! requires exactly 2 arguments"):
            seval(read_one("(set!)"), env)


class TestLambda:
    """Tests for the lambda special form."""

    def test_lambda_simple(self):
        env = make_global_env()
        expr = read_one("(lambda (x) (* x x))")
        result = seval(expr, env)
        assert isinstance(result, Procedure)
        assert len(result.params) == 1

    def test_lambda_call_simple(self):
        env = make_global_env()
        expr = read_one("((lambda (x) (* x x)) 5)")
        result = seval(expr, env)
        assert result == 25

    def test_lambda_multiple_params(self):
        env = make_global_env()
        expr = read_one("((lambda (x y) (+ x y)) 3 4)")
        result = seval(expr, env)
        assert result == 7

    def test_lambda_multiple_body_forms(self):
        env = make_global_env()
        expr = read_one("((lambda (x) (define y 10) (+ x y)) 5)")
        result = seval(expr, env)
        assert result == 15

    def test_lambda_closure(self):
        env = make_global_env()
        # Define a make-adder function that returns a lambda
        seval(read_one("(define make-adder (lambda (n) (lambda (x) (+ x n))))"), env)
        # Create an adder that adds 5
        seval(read_one("(define add5 (make-adder 5))"), env)
        # Test it
        result = seval(read_one("(add5 3)"), env)
        assert result == 8

    def test_lambda_arity_mismatch_too_few(self):
        env = make_global_env()
        expr = read_one("((lambda (x y) (+ x y)) 3)")
        with pytest.raises(EvalError, match="expected 2 arguments, got 1"):
            seval(expr, env)

    def test_lambda_arity_mismatch_too_many(self):
        env = make_global_env()
        expr = read_one("((lambda (x) x) 1 2)")
        with pytest.raises(EvalError, match="expected 1 arguments, got 2"):
            seval(expr, env)

    def test_lambda_no_params(self):
        env = make_global_env()
        expr = read_one("((lambda () 42))")
        result = seval(expr, env)
        assert result == 42

    def test_lambda_empty_body_returns_nil(self):
        env = make_global_env()
        expr = read_one("((lambda ()))")
        result = seval(expr, env)
        assert result is NIL


class TestLet:
    """Tests for the let special form."""

    def test_let_simple(self):
        env = make_global_env()
        expr = read_one("(let ((x 2) (y 3)) (+ x y))")
        result = seval(expr, env)
        assert result == 5

    def test_let_single_binding(self):
        env = make_global_env()
        expr = read_one("(let ((x 10)) x)")
        result = seval(expr, env)
        assert result == 10

    def test_let_multiple_body_forms(self):
        env = make_global_env()
        expr = read_one("(let ((x 1)) (define y 2) (+ x y))")
        result = seval(expr, env)
        assert result == 3

    def test_let_no_body_returns_nil(self):
        env = make_global_env()
        expr = read_one("(let ((x 10)))")
        result = seval(expr, env)
        assert result is NIL

    def test_let_expr_evaluated_in_current_env(self):
        env = make_global_env()
        seval(read_one("(define z 5)"), env)
        expr = read_one("(let ((x z)) (+ x 1))")
        result = seval(expr, env)
        assert result == 6

    def test_let_bindings_not_visible_outside(self):
        env = make_global_env()
        seval(read_one("(let ((x 10)))"), env)
        with pytest.raises(EvalError, match="undefined symbol"):
            seval(read_one("x"), env)

    def test_let_malformed_binding(self):
        env = make_global_env()
        expr = read_one("(let ((x)) 10)")
        with pytest.raises(EvalError, match="binding must be a"):
            seval(expr, env)


class TestBegin:
    """Tests for the begin special form."""

    def test_begin_returns_last_value(self):
        env = make_global_env()
        expr = read_one("(begin 1 2 3)")
        result = seval(expr, env)
        assert result == 3

    def test_begin_single_form(self):
        env = make_global_env()
        expr = read_one("(begin 42)")
        result = seval(expr, env)
        assert result == 42

    def test_begin_empty_returns_nil(self):
        env = make_global_env()
        expr = read_one("(begin)")
        result = seval(expr, env)
        assert result is NIL

    def test_begin_with_side_effects(self):
        env = make_global_env()
        expr = read_one("(begin (define x 10) (set! x 20) x)")
        result = seval(expr, env)
        assert result == 20


class TestListOperations:
    """Tests for list operations."""

    def test_list_empty(self):
        env = make_global_env()
        expr = read_one("(list)")
        result = seval(expr, env)
        assert result == NIL

    def test_list_multiple_elements(self):
        env = make_global_env()
        expr = read_one("(list 1 2 3)")
        result = seval(expr, env)
        assert list(result) == [1, 2, 3]

    def test_cons(self):
        env = make_global_env()
        expr = read_one("(cons 0 (list 1 2 3))")
        result = seval(expr, env)
        assert list(result) == [0, 1, 2, 3]

    def test_cons_to_empty_list(self):
        env = make_global_env()
        expr = read_one("(cons 5 nil)")
        result = seval(expr, env)
        assert list(result) == [5]

    def test_car(self):
        env = make_global_env()
        expr = read_one("(car (list 1 2 3))")
        result = seval(expr, env)
        assert result == 1

    def test_car_empty_list_raises_error(self):
        env = make_global_env()
        expr = read_one("(car nil)")
        with pytest.raises(EvalError, match="empty list has no car"):
            seval(expr, env)

    def test_cdr(self):
        env = make_global_env()
        expr = read_one("(cdr (list 1 2 3))")
        result = seval(expr, env)
        assert list(result) == [2, 3]

    def test_cdr_single_element(self):
        env = make_global_env()
        expr = read_one("(cdr (list 1))")
        result = seval(expr, env)
        assert result == NIL

    def test_cdr_empty_list_raises_error(self):
        env = make_global_env()
        expr = read_one("(cdr nil)")
        with pytest.raises(EvalError, match="empty list has no cdr"):
            seval(expr, env)

    def test_null_true(self):
        env = make_global_env()
        expr = read_one("(null? nil)")
        result = seval(expr, env)
        assert result is True

    def test_null_false(self):
        env = make_global_env()
        expr = read_one("(null? (list 1))")
        result = seval(expr, env)
        assert result is False


class TestRecursion:
    """Tests for recursive functions."""

    def test_factorial(self):
        env = make_global_env()
        # Define factorial
        seval(read_one("""
        (define factorial
          (lambda (n)
            (if (= n 0)
              1
              (* n (factorial (- n 1))))))
        """), env)
        # Test it
        result = seval(read_one("(factorial 5)"), env)
        assert result == 120

    def test_fibonacci(self):
        env = make_global_env()
        seval(read_one("""
        (define fib
          (lambda (n)
            (if (< n 2)
              n
              (+ (fib (- n 1)) (fib (- n 2))))))
        """), env)
        result = seval(read_one("(fib 6)"), env)
        assert result == 8


class TestEvalSource:
    """Tests for the eval_source function."""

    def test_eval_source_single_form(self):
        env = make_global_env()
        result = eval_source("42", env)
        assert result == 42

    def test_eval_source_multiple_forms(self):
        env = make_global_env()
        result = eval_source("(define x 10) (+ x 5)", env)
        assert result == 15

    def test_eval_source_empty(self):
        env = make_global_env()
        result = eval_source("", env)
        assert result is NIL

    def test_eval_source_comments(self):
        env = make_global_env()
        result = eval_source("; comment\n(+ 1 2)", env)
        assert result == 3


class TestErrors:
    """Tests for error handling."""

    def test_undefined_symbol(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="undefined symbol"):
            seval(read_one("undefined_var"), env)

    def test_not_callable(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="not callable"):
            seval(read_one("(42)"), env)

    def test_division_by_zero(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="division by zero"):
            seval(read_one("(/ 10 0)"), env)
