"""Tests for the Pebble standard library."""
import pytest
from pebble.evaluator import seval, make_global_env, eval_source, EvalError
from pebble.reader import read
from pebble.types import Symbol, PebbleList, NIL


class TestWhenMacro:
    """Tests for the when macro."""

    def test_when_with_truthy_test(self):
        env = make_global_env()
        result = eval_source("(when true 42)", env)
        assert result == 42

    def test_when_with_falsy_test(self):
        env = make_global_env()
        result = eval_source("(when false 42)", env)
        assert result == NIL

    def test_when_with_multiple_body_forms(self):
        env = make_global_env()
        result = eval_source("""
            (define x 0)
            (when true
              (set! x 1)
              (set! x (+ x 1))
              (+ x 10))
        """, env)
        assert result == 12

    def test_when_returns_nil_when_test_falsy(self):
        env = make_global_env()
        result = eval_source("(when false (+ 1 2))", env)
        assert result == NIL


class TestUnlessMacro:
    """Tests for the unless macro."""

    def test_unless_with_falsy_test(self):
        env = make_global_env()
        result = eval_source("(unless false 42)", env)
        assert result == 42

    def test_unless_with_truthy_test(self):
        env = make_global_env()
        result = eval_source("(unless true 42)", env)
        assert result == NIL

    def test_unless_with_multiple_body_forms(self):
        env = make_global_env()
        result = eval_source("""
            (define x 0)
            (unless false
              (set! x 1)
              (set! x (+ x 1))
              (+ x 10))
        """, env)
        assert result == 12


class TestAndMacro:
    """Tests for the and macro."""

    def test_and_empty_returns_true(self):
        env = make_global_env()
        result = eval_source("(and)", env)
        assert result is True

    def test_and_single_truthy(self):
        env = make_global_env()
        result = eval_source("(and 1)", env)
        assert result == 1

    def test_and_single_falsy(self):
        env = make_global_env()
        result = eval_source("(and false)", env)
        assert result is False

    def test_and_all_truthy(self):
        env = make_global_env()
        result = eval_source("(and 1 2 3)", env)
        assert result == 3

    def test_and_with_falsy_middle(self):
        env = make_global_env()
        result = eval_source("(and 1 false 3)", env)
        assert result is False

    def test_and_short_circuits(self):
        env = make_global_env()
        result = eval_source("""
            (define counter 0)
            (and false (begin (set! counter 1) true))
            counter
        """, env)
        # If short-circuiting works, counter should still be 0
        assert result == 0

    def test_and_does_not_short_circuit_on_truthy(self):
        env = make_global_env()
        result = eval_source("""
            (define counter 0)
            (and true (begin (set! counter 1) true))
            counter
        """, env)
        # counter should be 1 because both forms are evaluated
        assert result == 1

    def test_and_evaluates_falsy_argument_exactly_once(self):
        env = make_global_env()
        result = eval_source("""
            (define counter 0)
            (and true (begin (set! counter (+ counter 1)) false) 99)
            counter
        """, env)
        # counter should be 1 (the falsy argument is evaluated exactly once)
        assert result == 1


class TestOrMacro:
    """Tests for the or macro."""

    def test_or_empty_returns_false(self):
        env = make_global_env()
        result = eval_source("(or)", env)
        assert result is False

    def test_or_single_truthy(self):
        env = make_global_env()
        result = eval_source("(or 5)", env)
        assert result == 5

    def test_or_single_falsy(self):
        env = make_global_env()
        result = eval_source("(or false)", env)
        assert result is False

    def test_or_first_truthy(self):
        env = make_global_env()
        result = eval_source("(or false 5)", env)
        assert result == 5

    def test_or_all_falsy(self):
        env = make_global_env()
        result = eval_source("(or false false)", env)
        assert result is False

    def test_or_short_circuits(self):
        env = make_global_env()
        result = eval_source("""
            (define counter 0)
            (or true (begin (set! counter 1) false))
            counter
        """, env)
        # If short-circuiting works, counter should still be 0
        assert result == 0

    def test_or_does_not_double_evaluate_first_truthy(self):
        env = make_global_env()
        result = eval_source("""
            (define counter 0)
            (or (begin (set! counter 1) 5) false)
            counter
        """, env)
        # counter should be 1 (evaluated exactly once)
        assert result == 1


class TestCondMacro:
    """Tests for the cond macro."""

    def test_cond_first_clause_matches(self):
        env = make_global_env()
        result = eval_source("""
            (cond
              (true 42)
              (true 99))
        """, env)
        assert result == 42

    def test_cond_second_clause_matches(self):
        env = make_global_env()
        result = eval_source("""
            (cond
              (false 42)
              (true 99))
        """, env)
        assert result == 99

    def test_cond_no_match_returns_nil(self):
        env = make_global_env()
        result = eval_source("""
            (cond
              (false 42)
              (false 99))
        """, env)
        assert result == NIL

    def test_cond_else_clause(self):
        env = make_global_env()
        result = eval_source("""
            (cond
              (false 42)
              (else 99))
        """, env)
        assert result == 99

    def test_cond_clause_without_body_returns_test_value(self):
        env = make_global_env()
        result = eval_source("""
            (cond
              (false)
              (42))
        """, env)
        assert result == 42

    def test_cond_multiple_body_forms(self):
        env = make_global_env()
        result = eval_source("""
            (define x 0)
            (cond
              (true
                (set! x 1)
                (set! x (+ x 1))
                (+ x 10)))
        """, env)
        assert result == 12


class TestLetStar:
    """Tests for the let* macro."""

    def test_let_star_basic(self):
        env = make_global_env()
        result = eval_source("""
            (let* ((x 1))
              x)
        """, env)
        assert result == 1

    def test_let_star_sequential_binding(self):
        env = make_global_env()
        result = eval_source("""
            (let* ((x 1) (y (+ x 1)))
              y)
        """, env)
        assert result == 2

    def test_let_star_multiple_body_forms(self):
        env = make_global_env()
        result = eval_source("""
            (let* ((x 1) (y 2))
              (+ x y)
              (* x y))
        """, env)
        assert result == 2

    def test_let_star_nested_reference(self):
        env = make_global_env()
        result = eval_source("""
            (let* ((a 1) (b (+ a 1)) (c (+ b 1)))
              c)
        """, env)
        assert result == 3


class TestAccessors:
    """Tests for list accessors."""

    def test_caar(self):
        env = make_global_env()
        result = eval_source("(caar (list (list 1 2) 3))", env)
        assert result == 1

    def test_cadr(self):
        env = make_global_env()
        result = eval_source("(cadr (list 1 2 3))", env)
        assert result == 2

    def test_caddr(self):
        env = make_global_env()
        result = eval_source("(caddr (list 1 2 3))", env)
        assert result == 3

    def test_cddr(self):
        env = make_global_env()
        result = eval_source("(cddr (list 1 2 3))", env)
        assert isinstance(result, PebbleList)
        assert list(result) == [3]

    def test_first(self):
        env = make_global_env()
        result = eval_source("(first (list 1 2 3))", env)
        assert result == 1

    def test_second(self):
        env = make_global_env()
        result = eval_source("(second (list 1 2 3))", env)
        assert result == 2

    def test_third(self):
        env = make_global_env()
        result = eval_source("(third (list 1 2 3))", env)
        assert result == 3

    def test_rest(self):
        env = make_global_env()
        result = eval_source("(rest (list 1 2 3))", env)
        assert isinstance(result, PebbleList)
        assert list(result) == [2, 3]


class TestIdentity:
    """Tests for identity function."""

    def test_identity_number(self):
        env = make_global_env()
        result = eval_source("(identity 42)", env)
        assert result == 42

    def test_identity_list(self):
        env = make_global_env()
        result = eval_source("(identity (list 1 2 3))", env)
        assert isinstance(result, PebbleList)
        assert list(result) == [1, 2, 3]


class TestIncDec:
    """Tests for inc and dec functions."""

    def test_inc(self):
        env = make_global_env()
        result = eval_source("(inc 5)", env)
        assert result == 6

    def test_dec(self):
        env = make_global_env()
        result = eval_source("(dec 5)", env)
        assert result == 4

    def test_inc_negative(self):
        env = make_global_env()
        result = eval_source("(inc -1)", env)
        assert result == 0

    def test_dec_negative(self):
        env = make_global_env()
        result = eval_source("(dec -1)", env)
        assert result == -2


class TestNumericPredicates:
    """Tests for numeric predicates."""

    def test_zero_true(self):
        env = make_global_env()
        result = eval_source("(zero? 0)", env)
        assert result is True

    def test_zero_false(self):
        env = make_global_env()
        result = eval_source("(zero? 1)", env)
        assert result is False

    def test_positive_true(self):
        env = make_global_env()
        result = eval_source("(positive? 5)", env)
        assert result is True

    def test_positive_false(self):
        env = make_global_env()
        result = eval_source("(positive? -1)", env)
        assert result is False

    def test_negative_true(self):
        env = make_global_env()
        result = eval_source("(negative? -5)", env)
        assert result is True

    def test_negative_false(self):
        env = make_global_env()
        result = eval_source("(negative? 1)", env)
        assert result is False

    def test_even_true(self):
        env = make_global_env()
        result = eval_source("(even? 4)", env)
        assert result is True

    def test_even_false(self):
        env = make_global_env()
        result = eval_source("(even? 3)", env)
        assert result is False

    def test_odd_true(self):
        env = make_global_env()
        result = eval_source("(odd? 3)", env)
        assert result is True

    def test_odd_false(self):
        env = make_global_env()
        result = eval_source("(odd? 4)", env)
        assert result is False


class TestCompose:
    """Tests for compose function."""

    def test_compose_basic(self):
        env = make_global_env()
        result = eval_source("((compose inc inc) 5)", env)
        assert result == 7

    def test_compose_with_arithmetic(self):
        env = make_global_env()
        result = eval_source("""
            (define double (lambda (x) (* x 2)))
            ((compose inc double) 3)
        """, env)
        assert result == 7


class TestConst:
    """Tests for const function."""

    def test_const_returns_same_value(self):
        env = make_global_env()
        result = eval_source("((const 42) 100)", env)
        assert result == 42

    def test_const_with_different_args(self):
        env = make_global_env()
        result = eval_source("""
            (define f (const 99))
            (list (f 1) (f 2) (f 3))
        """, env)
        assert list(result) == [99, 99, 99]


class TestLast:
    """Tests for last function."""

    def test_last_single_element(self):
        env = make_global_env()
        result = eval_source("(last (list 42))", env)
        assert result == 42

    def test_last_multiple_elements(self):
        env = make_global_env()
        result = eval_source("(last (list 1 2 3 4 5))", env)
        assert result == 5


class TestNth:
    """Tests for nth function."""

    def test_nth_first_element(self):
        env = make_global_env()
        result = eval_source("(nth (list 1 2 3) 0)", env)
        assert result == 1

    def test_nth_middle_element(self):
        env = make_global_env()
        result = eval_source("(nth (list 1 2 3) 1)", env)
        assert result == 2

    def test_nth_last_element(self):
        env = make_global_env()
        result = eval_source("(nth (list 1 2 3) 2)", env)
        assert result == 3


class TestRange:
    """Tests for range function."""

    def test_range_single_arg(self):
        env = make_global_env()
        result = eval_source("(range 5)", env)
        assert list(result) == [0, 1, 2, 3, 4]

    def test_range_empty(self):
        env = make_global_env()
        result = eval_source("(range 0)", env)
        assert result == NIL

    def test_range_two_args(self):
        env = make_global_env()
        result = eval_source("(range 2 5)", env)
        assert list(result) == [2, 3, 4]

    def test_range_two_args_equal(self):
        env = make_global_env()
        result = eval_source("(range 5 5)", env)
        assert result == NIL

    def test_range_large(self):
        env = make_global_env()
        result = eval_source("(length (range 5000))", env)
        assert result == 5000

    def test_range_preserves_order(self):
        env = make_global_env()
        result = eval_source("(range 10)", env)
        assert list(result) == list(range(10))


class TestTakeDrop:
    """Tests for take and drop functions."""

    def test_take_basic(self):
        env = make_global_env()
        result = eval_source("(take (list 1 2 3 4 5) 2)", env)
        assert list(result) == [1, 2]

    def test_take_all(self):
        env = make_global_env()
        result = eval_source("(take (list 1 2 3) 3)", env)
        assert list(result) == [1, 2, 3]

    def test_take_more_than_list(self):
        env = make_global_env()
        result = eval_source("(take (list 1 2) 5)", env)
        assert list(result) == [1, 2]

    def test_take_zero(self):
        env = make_global_env()
        result = eval_source("(take (list 1 2 3) 0)", env)
        assert result == NIL

    def test_drop_basic(self):
        env = make_global_env()
        result = eval_source("(drop (list 1 2 3 4 5) 2)", env)
        assert list(result) == [3, 4, 5]

    def test_drop_all(self):
        env = make_global_env()
        result = eval_source("(drop (list 1 2 3) 3)", env)
        assert result == NIL

    def test_drop_zero(self):
        env = make_global_env()
        result = eval_source("(drop (list 1 2 3) 0)", env)
        assert list(result) == [1, 2, 3]


class TestSumProduct:
    """Tests for sum and product functions."""

    def test_sum_basic(self):
        env = make_global_env()
        result = eval_source("(sum (list 1 2 3 4))", env)
        assert result == 10

    def test_sum_empty(self):
        env = make_global_env()
        result = eval_source("(sum (list))", env)
        assert result == 0

    def test_product_basic(self):
        env = make_global_env()
        result = eval_source("(product (list 2 3 4))", env)
        assert result == 24

    def test_product_empty(self):
        env = make_global_env()
        result = eval_source("(product (list))", env)
        assert result == 1


class TestReduce:
    """Tests for reduce function."""

    def test_reduce_basic(self):
        env = make_global_env()
        result = eval_source("(reduce + (list 1 2 3 4))", env)
        assert result == 10

    def test_reduce_single_element(self):
        env = make_global_env()
        result = eval_source("(reduce + (list 5))", env)
        assert result == 5

    def test_reduce_empty_raises_error(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="reduce: empty list"):
            eval_source("(reduce + (list))", env)


class TestMap2:
    """Tests for map2 function."""

    def test_map2_basic(self):
        env = make_global_env()
        result = eval_source("(map2 + (list 1 2 3) (list 10 20 30))", env)
        assert list(result) == [11, 22, 33]

    def test_map2_different_lengths(self):
        env = make_global_env()
        result = eval_source("(map2 + (list 1 2) (list 10 20 30))", env)
        assert list(result) == [11, 22]


class TestZip:
    """Tests for zip function."""

    def test_zip_basic(self):
        env = make_global_env()
        result = eval_source("(zip (list 1 2 3) (list 4 5 6))", env)
        # Result is a list of lists
        result_list = [list(x) for x in result]
        assert result_list == [[1, 4], [2, 5], [3, 6]]


class TestFlatten:
    """Tests for flatten function."""

    def test_flatten_simple(self):
        env = make_global_env()
        result = eval_source("(flatten (list 1 2 3))", env)
        assert list(result) == [1, 2, 3]

    def test_flatten_nested(self):
        env = make_global_env()
        result = eval_source("(flatten (list 1 (list 2 3) 4))", env)
        assert list(result) == [1, 2, 3, 4]

    def test_flatten_deeply_nested(self):
        env = make_global_env()
        result = eval_source("(flatten (list 1 (list 2 (list 3 4)) 5))", env)
        assert list(result) == [1, 2, 3, 4, 5]


class TestStringJoin:
    """Tests for string-join function."""

    def test_string_join_basic(self):
        env = make_global_env()
        result = eval_source('(string-join (list "a" "b" "c") ",")', env)
        assert result == "a,b,c"

    def test_string_join_empty(self):
        env = make_global_env()
        result = eval_source('(string-join (list) ",")', env)
        assert result == ""

    def test_string_join_single(self):
        env = make_global_env()
        result = eval_source('(string-join (list "hello") ",")', env)
        assert result == "hello"

    def test_string_join_space_separator(self):
        env = make_global_env()
        result = eval_source('(string-join (list "hello" "world") " ")', env)
        assert result == "hello world"


class TestDisplayln:
    """Tests for displayln function."""

    def test_displayln_returns_nil(self, capsys):
        env = make_global_env()
        result = eval_source("(displayln 42)", env)
        assert result == NIL
        captured = capsys.readouterr()
        assert "42" in captured.out
        assert "\n" in captured.out


class TestPreludeLoader:
    """Tests for the prelude loader mechanism."""

    def test_make_global_env_loads_prelude_by_default(self):
        from pebble.evaluator import Procedure
        env = make_global_env()
        # Try to use a prelude function
        result = seval(Symbol("inc"), env)
        # Should not raise EvalError and should be a Procedure or callable
        assert isinstance(result, Procedure) or callable(result)

    def test_make_global_env_with_load_prelude_false(self):
        env = make_global_env(load_prelude=False)
        # Try to look up a prelude function
        with pytest.raises(EvalError, match="undefined symbol"):
            seval(Symbol("inc"), env)

    def test_make_global_env_false_still_has_builtins(self):
        env = make_global_env(load_prelude=False)
        # Primitives like + should still be available
        result = seval(Symbol("+"), env)
        assert callable(result)

    def test_prelude_names_can_be_redefined(self):
        env = make_global_env()
        # Redefine a prelude function
        eval_source("(define (when x) (+ x 1))", env)
        result = seval(Symbol("when"), env)
        # Should be the new definition (a procedure)
        from pebble.evaluator import Procedure
        assert isinstance(result, Procedure)

    def test_when_is_in_prelude(self):
        env = make_global_env()
        result = eval_source("(when true 99)", env)
        assert result == 99

    def test_range_is_in_prelude(self):
        env = make_global_env()
        result = eval_source("(range 3)", env)
        assert list(result) == [0, 1, 2]
