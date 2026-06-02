"""Tests for match pattern-matching macro."""
import pytest
from pebble.evaluator import make_global_env, seval, EvalError
from pebble.types import Symbol, PebbleList, NIL


class TestMatchLiterals:
    """Test literal pattern matching."""

    def test_match_number_literal_true(self):
        """Test (match 5 (5 "five") (_ "other")) -> "five"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                5,
                PebbleList([5, "five"]),
                PebbleList([Symbol("_"), "other"])
            ]),
            env
        )
        assert result == "five"

    def test_match_number_literal_false(self):
        """Test (match 6 (5 "five") (_ "other")) -> "other"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                6,
                PebbleList([5, "five"]),
                PebbleList([Symbol("_"), "other"])
            ]),
            env
        )
        assert result == "other"

    def test_match_string_literal(self):
        """Test matching string literals."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                "hello",
                PebbleList(["hello", "is-hello"]),
                PebbleList([Symbol("_"), "other"])
            ]),
            env
        )
        assert result == "is-hello"

    def test_match_boolean_literal(self):
        """Test matching boolean literals."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                True,
                PebbleList([True, "is-true"]),
                PebbleList([False, "is-false"])
            ]),
            env
        )
        assert result == "is-true"


class TestMatchVariable:
    """Test variable binding in patterns."""

    def test_match_variable_bind(self):
        """Test (match 42 (x (+ x 1))) -> 43."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                42,
                PebbleList([
                    Symbol("x"),
                    PebbleList([Symbol("+"), Symbol("x"), 1])
                ])
            ]),
            env
        )
        assert result == 43

    def test_match_variable_returns_value(self):
        """Test (match 99 (x x)) -> 99."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                99,
                PebbleList([Symbol("x"), Symbol("x")])
            ]),
            env
        )
        assert result == 99


class TestMatchWildcard:
    """Test wildcard (_) pattern."""

    def test_match_wildcard(self):
        """Test (match 99 (_ "anything")) -> "anything"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                99,
                PebbleList([Symbol("_"), "anything"])
            ]),
            env
        )
        assert result == "anything"

    def test_match_wildcard_ignores_value(self):
        """Test wildcard doesn't bind the value."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                42,
                PebbleList([Symbol("_"), 100])
            ]),
            env
        )
        assert result == 100


class TestMatchNil:
    """Test nil pattern matching."""

    def test_match_nil_pattern_true(self):
        """Test (match nil (nil "empty") (_ "no")) -> "empty"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                NIL,
                PebbleList([NIL, "empty"]),
                PebbleList([Symbol("_"), "no"])
            ]),
            env
        )
        assert result == "empty"

    def test_match_nil_pattern_false(self):
        """Test (match (list 1) (nil "empty") (_ "no")) -> "no"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 1]),
                PebbleList([NIL, "empty"]),
                PebbleList([Symbol("_"), "no"])
            ]),
            env
        )
        assert result == "no"


class TestMatchFixedList:
    """Test fixed-length list pattern matching."""

    def test_match_fixed_list_simple(self):
        """Test (match (list 1 2 3) ((a b c) (+ a b c))) -> 6."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 1, 2, 3]),
                PebbleList([
                    PebbleList([Symbol("a"), Symbol("b"), Symbol("c")]),
                    PebbleList([Symbol("+"), PebbleList([Symbol("+"), Symbol("a"), Symbol("b")]), Symbol("c")])
                ])
            ]),
            env
        )
        assert result == 6

    def test_match_fixed_list_length_mismatch(self):
        """Test length mismatch falls through: (match (list 1 2) ((a b c) "three") (_ "other")) -> "other"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 1, 2]),
                PebbleList([
                    PebbleList([Symbol("a"), Symbol("b"), Symbol("c")]),
                    "three"
                ]),
                PebbleList([Symbol("_"), "other"])
            ]),
            env
        )
        assert result == "other"


class TestMatchError:
    """Test error handling for no matching clause."""

    def test_match_no_match_raises_error(self):
        """Test (match 5 (6 "six")) raises error."""
        env = make_global_env()
        with pytest.raises(EvalError) as exc_info:
            seval(
                PebbleList([
                    Symbol("match"),
                    5,
                    PebbleList([6, "six"])
                ]),
                env
            )
        assert "no matching clause" in str(exc_info.value)

    def test_match_no_match_with_multiple_clauses(self):
        """Test error when no clause matches with multiple clauses."""
        env = make_global_env()
        with pytest.raises(EvalError) as exc_info:
            seval(
                PebbleList([
                    Symbol("match"),
                    5,
                    PebbleList([1, "one"]),
                    PebbleList([2, "two"]),
                    PebbleList([3, "three"])
                ]),
                env
            )
        assert "no matching clause" in str(exc_info.value)


class TestMatchSingleEvaluation:
    """Test that scrutinee expression is evaluated exactly once."""

    def test_match_scrutinee_evaluated_once(self):
        """Test scrutinee is evaluated exactly once even though multiple clauses are tried."""
        env = make_global_env()
        # Use a counter variable to track evaluations
        seval(
            PebbleList([
                Symbol("define"),
                Symbol("counter"),
                0
            ]),
            env
        )

        # Create a function that increments the counter and returns something unique
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([
                    Symbol("begin"),
                    PebbleList([Symbol("set!"), Symbol("counter"), PebbleList([Symbol("+"), Symbol("counter"), 1])]),
                    Symbol("counter")
                ]),
                PebbleList([Symbol("x"), Symbol("x")])  # x matches anything and returns the value
            ]),
            env
        )

        # Result should be 1 (the counter value)
        assert result == 1

        # Verify counter was only incremented once
        counter = seval(Symbol("counter"), env)
        assert counter == 1
