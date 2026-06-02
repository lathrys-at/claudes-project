"""Tests for define function-definition shorthand."""
import pytest
from pebble.evaluator import seval, make_global_env, EvalError
from pebble.types import Symbol, PebbleList


def test_define_shorthand_simple():
    """Test (define (sq x) (* x x)) then (sq 5) -> 25."""
    env = make_global_env()
    seval(PebbleList([
        Symbol("define"),
        PebbleList([Symbol("sq"), Symbol("x")]),
        PebbleList([Symbol("*"), Symbol("x"), Symbol("x")])
    ]), env)
    result = seval(PebbleList([Symbol("sq"), 5]), env)
    assert result == 25


def test_define_shorthand_zero_params():
    """Test (define (answer) 42) then (answer) -> 42."""
    env = make_global_env()
    seval(PebbleList([
        Symbol("define"),
        PebbleList([Symbol("answer")]),
        42
    ]), env)
    result = seval(PebbleList([Symbol("answer")]), env)
    assert result == 42


def test_define_shorthand_multi_form_body():
    """Test (define (f x) (define y (* x 2)) (+ y 1)) then (f 10) -> 21."""
    env = make_global_env()
    seval(PebbleList([
        Symbol("define"),
        PebbleList([Symbol("f"), Symbol("x")]),
        PebbleList([Symbol("define"), Symbol("y"), PebbleList([Symbol("*"), Symbol("x"), 2])]),
        PebbleList([Symbol("+"), Symbol("y"), 1])
    ]), env)
    result = seval(PebbleList([Symbol("f"), 10]), env)
    assert result == 21


def test_define_shorthand_variadic_rest():
    """Test (define (g a . rest) rest) then (g 1 2 3) -> (2 3)."""
    env = make_global_env()
    seval(PebbleList([
        Symbol("define"),
        PebbleList([Symbol("g"), Symbol("a"), Symbol("."), Symbol("rest")]),
        Symbol("rest")
    ]), env)
    result = seval(PebbleList([Symbol("g"), 1, 2, 3]), env)
    assert isinstance(result, PebbleList)
    assert list(result) == [2, 3]


def test_define_shorthand_variadic_all():
    """Test (define (h . xs) xs) then (h 1 2) -> (1 2)."""
    env = make_global_env()
    seval(PebbleList([
        Symbol("define"),
        PebbleList([Symbol("h"), Symbol("."), Symbol("xs")]),
        Symbol("xs")
    ]), env)
    result = seval(PebbleList([Symbol("h"), 1, 2]), env)
    assert isinstance(result, PebbleList)
    assert list(result) == [1, 2]


def test_define_shorthand_returns_name():
    """Test that shorthand returns the function name symbol."""
    env = make_global_env()
    result = seval(PebbleList([
        Symbol("define"),
        PebbleList([Symbol("foo"), Symbol("x")]),
        Symbol("x")
    ]), env)
    assert result == Symbol("foo")


def test_define_shorthand_recursion():
    """Test recursion: factorial defined with shorthand."""
    env = make_global_env()
    # (define (fact n) (if (< n 2) 1 (* n (fact (- n 1)))))
    seval(PebbleList([
        Symbol("define"),
        PebbleList([Symbol("fact"), Symbol("n")]),
        PebbleList([
            Symbol("if"),
            PebbleList([Symbol("<"), Symbol("n"), 2]),
            1,
            PebbleList([Symbol("*"), Symbol("n"), PebbleList([Symbol("fact"), PebbleList([Symbol("-"), Symbol("n"), 1])])])
        ])
    ]), env)
    result = seval(PebbleList([Symbol("fact"), 5]), env)
    assert result == 120


def test_define_shorthand_tail_recursion():
    """Test tail-call optimization: tail-recursive loop at 100,000 iterations."""
    env = make_global_env()
    # (define (loop n acc) (if (<= n 0) acc (loop (- n 1) (+ acc 1))))
    seval(PebbleList([
        Symbol("define"),
        PebbleList([Symbol("loop"), Symbol("n"), Symbol("acc")]),
        PebbleList([
            Symbol("if"),
            PebbleList([Symbol("<="), Symbol("n"), 0]),
            Symbol("acc"),
            PebbleList([Symbol("loop"), PebbleList([Symbol("-"), Symbol("n"), 1]), PebbleList([Symbol("+"), Symbol("acc"), 1])])
        ])
    ]), env)
    result = seval(PebbleList([Symbol("loop"), 100000, 0]), env)
    assert result == 100000


def test_define_value_form_still_works():
    """Test that value form still works: (define z 7) then z -> 7."""
    env = make_global_env()
    result1 = seval(PebbleList([Symbol("define"), Symbol("z"), 7]), env)
    assert result1 == Symbol("z")
    result2 = seval(Symbol("z"), env)
    assert result2 == 7


def test_define_shorthand_non_symbol_name():
    """Test error: non-symbol function name."""
    env = make_global_env()
    with pytest.raises(EvalError) as exc_info:
        seval(PebbleList([
            Symbol("define"),
            PebbleList([42, Symbol("x")]),
            Symbol("x")
        ]), env)
    assert "must be a symbol" in str(exc_info.value)


def test_define_shorthand_empty_list():
    """Test error: (define ()) raises EvalError."""
    env = make_global_env()
    with pytest.raises(EvalError) as exc_info:
        seval(PebbleList([
            Symbol("define"),
            PebbleList([])
        ]), env)
    assert "cannot be empty" in str(exc_info.value)


def test_define_shorthand_malformed_params():
    """Test error: malformed parameter specification."""
    env = make_global_env()
    with pytest.raises(EvalError) as exc_info:
        seval(PebbleList([
            Symbol("define"),
            PebbleList([Symbol("f"), Symbol("."), Symbol("a"), Symbol("b")]),
            Symbol("a")
        ]), env)
    assert "malformed" in str(exc_info.value) or "rest" in str(exc_info.value)


def test_define_value_form_wrong_arity():
    """Test error: value form with wrong arity."""
    env = make_global_env()
    with pytest.raises(EvalError) as exc_info:
        seval(PebbleList([
            Symbol("define"),
            Symbol("x"),
            1,
            2
        ]), env)
    assert "exactly 2 arguments" in str(exc_info.value)
