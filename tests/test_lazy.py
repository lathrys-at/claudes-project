"""Tests for lazy evaluation (delay, force, promise?)."""
import pytest
from pebble.evaluator import seval, make_global_env, EvalError
from pebble.types import Symbol, PebbleList


def test_basic_delay_force():
    """Test (force (delay (+ 1 2))) -> 3."""
    env = make_global_env()
    result = seval(
        PebbleList([
            Symbol("force"),
            PebbleList([
                Symbol("delay"),
                PebbleList([Symbol("+"), 1, 2])
            ])
        ]),
        env
    )
    assert result == 3


def test_deferral_not_evaluated_immediately():
    """Test that delay does NOT evaluate its expression immediately.

    Setup: (define count 0)
           (define p (delay (begin (set! count (+ count 1)) 42)))
    Before force: count should be 0
    After force: result should be 42 and count should be 1
    """
    env = make_global_env()

    # Define count = 0
    seval(PebbleList([Symbol("define"), Symbol("count"), 0]), env)

    # Define p = (delay (begin (set! count (+ count 1)) 42))
    seval(PebbleList([
        Symbol("define"),
        Symbol("p"),
        PebbleList([
            Symbol("delay"),
            PebbleList([
                Symbol("begin"),
                PebbleList([Symbol("set!"), Symbol("count"), PebbleList([Symbol("+"), Symbol("count"), 1])]),
                42
            ])
        ])
    ]), env)

    # Check count is still 0 before forcing
    count_before = seval(Symbol("count"), env)
    assert count_before == 0, "Expression in delay was evaluated immediately!"

    # Force the promise
    result = seval(PebbleList([Symbol("force"), Symbol("p")]), env)
    assert result == 42

    # Check count is now 1
    count_after = seval(Symbol("count"), env)
    assert count_after == 1


def test_memoization_single_evaluation():
    """Test that forcing the same promise multiple times does not re-evaluate.

    Setup: (define count 0)
           (define p (delay (begin (set! count (+ count 1)) 42)))
    After first force: result is 42, count is 1
    After second force: result is 42, count is still 1 (not re-evaluated)
    """
    env = make_global_env()

    # Define count = 0
    seval(PebbleList([Symbol("define"), Symbol("count"), 0]), env)

    # Define p = (delay (begin (set! count (+ count 1)) 42))
    seval(PebbleList([
        Symbol("define"),
        Symbol("p"),
        PebbleList([
            Symbol("delay"),
            PebbleList([
                Symbol("begin"),
                PebbleList([Symbol("set!"), Symbol("count"), PebbleList([Symbol("+"), Symbol("count"), 1])]),
                42
            ])
        ])
    ]), env)

    # Force the promise first time
    result1 = seval(PebbleList([Symbol("force"), Symbol("p")]), env)
    assert result1 == 42

    count_after_first = seval(Symbol("count"), env)
    assert count_after_first == 1

    # Force the promise second time
    result2 = seval(PebbleList([Symbol("force"), Symbol("p")]), env)
    assert result2 == 42

    # count should still be 1 (not re-evaluated)
    count_after_second = seval(Symbol("count"), env)
    assert count_after_second == 1, "Promise was re-evaluated on second force!"


def test_promise_predicate_true_for_delayed():
    """Test (promise? (delay 5)) -> true."""
    env = make_global_env()
    result = seval(
        PebbleList([
            Symbol("promise?"),
            PebbleList([Symbol("delay"), 5])
        ]),
        env
    )
    assert result is True


def test_promise_predicate_false_for_number():
    """Test (promise? 5) -> false."""
    env = make_global_env()
    result = seval(PebbleList([Symbol("promise?"), 5]), env)
    assert result is False


def test_promise_predicate_false_for_string():
    """Test (promise? \"hello\") -> false."""
    env = make_global_env()
    result = seval(PebbleList([Symbol("promise?"), "hello"]), env)
    assert result is False


def test_promise_predicate_false_for_vector():
    """Test (promise? (vector 1 2 3)) -> false.

    Even though the internal representation is a vector,
    promise? should reject ordinary vectors.
    """
    env = make_global_env()
    result = seval(
        PebbleList([
            Symbol("promise?"),
            PebbleList([Symbol("vector"), 1, 2, 3])
        ]),
        env
    )
    assert result is False


def test_promise_predicate_false_for_list():
    """Test (promise? (list 1 2)) -> false."""
    env = make_global_env()
    result = seval(
        PebbleList([
            Symbol("promise?"),
            PebbleList([Symbol("list"), 1, 2])
        ]),
        env
    )
    assert result is False


def test_force_non_promise_returns_unchanged():
    """Test (force 42) -> 42."""
    env = make_global_env()
    result = seval(PebbleList([Symbol("force"), 42]), env)
    assert result == 42


def test_force_non_promise_string():
    """Test (force \"hi\") -> \"hi\"."""
    env = make_global_env()
    result = seval(PebbleList([Symbol("force"), "hi"]), env)
    assert result == "hi"


def test_force_non_promise_list():
    """Test (force (list 1 2 3)) -> (1 2 3)."""
    env = make_global_env()
    result = seval(
        PebbleList([
            Symbol("force"),
            PebbleList([Symbol("list"), 1, 2, 3])
        ]),
        env
    )
    expected = PebbleList([1, 2, 3])
    assert result == expected


def test_lexical_capture():
    """Test that delay captures the lexical environment.

    (let ((x 10)) (force (delay (* x x)))) -> 100
    """
    env = make_global_env()
    result = seval(
        PebbleList([
            Symbol("let"),
            PebbleList([PebbleList([Symbol("x"), 10])]),
            PebbleList([
                Symbol("force"),
                PebbleList([
                    Symbol("delay"),
                    PebbleList([Symbol("*"), Symbol("x"), Symbol("x")])
                ])
            ])
        ]),
        env
    )
    assert result == 100


def test_nested_promises():
    """Test (force (delay (force (delay 7)))) -> 7."""
    env = make_global_env()
    result = seval(
        PebbleList([
            Symbol("force"),
            PebbleList([
                Symbol("delay"),
                PebbleList([
                    Symbol("force"),
                    PebbleList([
                        Symbol("delay"),
                        7
                    ])
                ])
            ])
        ]),
        env
    )
    assert result == 7


def test_force_with_side_effects():
    """Test that side effects in a promise only happen once.

    (define results (list))
    (define p (delay (begin (set! results (cons 1 results)) 42)))
    (force p)  -> 42, results = (1)
    (force p)  -> 42, results = (1) (no change)
    """
    env = make_global_env()

    # Define results = (list) (empty list)
    seval(PebbleList([Symbol("define"), Symbol("results"), PebbleList([Symbol("list")])]), env)

    # Define p = (delay (begin (set! results (cons 1 results)) 42))
    seval(PebbleList([
        Symbol("define"),
        Symbol("p"),
        PebbleList([
            Symbol("delay"),
            PebbleList([
                Symbol("begin"),
                PebbleList([Symbol("set!"), Symbol("results"), PebbleList([Symbol("cons"), 1, Symbol("results")])]),
                42
            ])
        ])
    ]), env)

    # Force first time
    result1 = seval(PebbleList([Symbol("force"), Symbol("p")]), env)
    assert result1 == 42

    results_after_first = seval(Symbol("results"), env)
    # results should be (1)
    assert results_after_first == PebbleList([1])

    # Force second time
    result2 = seval(PebbleList([Symbol("force"), Symbol("p")]), env)
    assert result2 == 42

    # results should still be (1), not (1 1)
    results_after_second = seval(Symbol("results"), env)
    assert results_after_second == PebbleList([1]), "Side effect happened twice!"


def test_delayed_computation_with_variable_references():
    """Test that delay properly captures variable references.

    (define x 5)
    (define p (delay (* x 2)))
    x = 5, (force p) = 10
    (set! x 20)
    (force p) = 40 (uses new value of x)
    """
    env = make_global_env()

    # Define x = 5
    seval(PebbleList([Symbol("define"), Symbol("x"), 5]), env)

    # Define p = (delay (* x 2))
    seval(PebbleList([
        Symbol("define"),
        Symbol("p"),
        PebbleList([
            Symbol("delay"),
            PebbleList([Symbol("*"), Symbol("x"), 2])
        ])
    ]), env)

    # First force with x = 5
    result1 = seval(PebbleList([Symbol("force"), Symbol("p")]), env)
    assert result1 == 10

    # Change x
    seval(PebbleList([Symbol("set!"), Symbol("x"), 20]), env)

    # Force again - should use cached value (10), not recompute with new x
    result2 = seval(PebbleList([Symbol("force"), Symbol("p")]), env)
    assert result2 == 10, "Promise was re-evaluated after variable change!"


def test_promise_with_arithmetic():
    """Test (force (delay (+ 10 20 30))) -> 60."""
    env = make_global_env()
    result = seval(
        PebbleList([
            Symbol("force"),
            PebbleList([
                Symbol("delay"),
                PebbleList([Symbol("+"), 10, 20, 30])
            ])
        ]),
        env
    )
    assert result == 60


def test_multiple_promises_independent():
    """Test that multiple promises are independent.

    (define p1 (delay (+ 1 2)))
    (define p2 (delay (* 3 4)))
    (force p1) -> 3
    (force p2) -> 12
    """
    env = make_global_env()

    # Define p1 and p2
    seval(PebbleList([
        Symbol("define"),
        Symbol("p1"),
        PebbleList([Symbol("delay"), PebbleList([Symbol("+"), 1, 2])])
    ]), env)

    seval(PebbleList([
        Symbol("define"),
        Symbol("p2"),
        PebbleList([Symbol("delay"), PebbleList([Symbol("*"), 3, 4])])
    ]), env)

    # Force both
    result1 = seval(PebbleList([Symbol("force"), Symbol("p1")]), env)
    result2 = seval(PebbleList([Symbol("force"), Symbol("p2")]), env)

    assert result1 == 3
    assert result2 == 12
