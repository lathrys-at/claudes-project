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


class TestMatchQuotedSymbol:
    """Test quoted-symbol pattern matching."""

    def test_match_quoted_symbol_positive(self):
        """Test (match (quote foo) ((quote foo) "yes") (_ "no")) -> "yes"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("quote"), Symbol("foo")]),
                PebbleList([PebbleList([Symbol("quote"), Symbol("foo")]), "yes"]),
                PebbleList([Symbol("_"), "no"])
            ]),
            env
        )
        assert result == "yes"

    def test_match_quoted_symbol_negative(self):
        """Test (match (quote bar) ((quote foo) "yes") (_ "no")) -> "no"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("quote"), Symbol("bar")]),
                PebbleList([PebbleList([Symbol("quote"), Symbol("foo")]), "yes"]),
                PebbleList([Symbol("_"), "no"])
            ]),
            env
        )
        assert result == "no"


class TestMatchNestedBinding:
    """Test nested variable binding in list patterns."""

    def test_match_nested_binding_two_levels(self):
        """Test (match (list 1 (list 2 3)) ((a (b c)) (+ a b c))) -> 6."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 1, PebbleList([Symbol("list"), 2, 3])]),
                PebbleList([
                    PebbleList([Symbol("a"), PebbleList([Symbol("b"), Symbol("c")])]),
                    PebbleList([Symbol("+"), PebbleList([Symbol("+"), Symbol("a"), Symbol("b")]), Symbol("c")])
                ])
            ]),
            env
        )
        assert result == 6

    def test_match_deeply_nested_binding(self):
        """Test deeply nested patterns with recursive binding."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 1, PebbleList([Symbol("list"), 2, PebbleList([Symbol("list"), 3, 4])])]),
                PebbleList([
                    PebbleList([
                        Symbol("a"),
                        PebbleList([
                            Symbol("b"),
                            PebbleList([Symbol("c"), Symbol("d")])
                        ])
                    ]),
                    PebbleList([
                        Symbol("+"),
                        PebbleList([
                            Symbol("+"),
                            PebbleList([Symbol("+"), Symbol("a"), Symbol("b")]),
                            Symbol("c")
                        ]),
                        Symbol("d")
                    ])
                ])
            ]),
            env
        )
        assert result == 10


class TestMatchNestedMismatch:
    """Test that nested mismatches cause fallthrough."""

    def test_match_nested_length_mismatch(self):
        """Test (match (list 1 (list 2 3 4)) ((a (b c)) "inner3") (_ "other")) -> "other"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 1, PebbleList([Symbol("list"), 2, 3, 4])]),
                PebbleList([
                    PebbleList([Symbol("a"), PebbleList([Symbol("b"), Symbol("c")])]),
                    "inner3"
                ]),
                PebbleList([Symbol("_"), "other"])
            ]),
            env
        )
        assert result == "other"


class TestMatchNonListVsList:
    """Test that non-list values do not match list patterns (no error)."""

    def test_match_atom_vs_list_pattern(self):
        """Test (match 5 ((a b) "list") (_ "atom")) -> "atom"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                5,
                PebbleList([PebbleList([Symbol("a"), Symbol("b")]), "list"]),
                PebbleList([Symbol("_"), "atom"])
            ]),
            env
        )
        assert result == "atom"

    def test_match_string_vs_list_pattern(self):
        """Test (match "hello" ((a b) "list") (_ "string")) -> "string"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                "hello",
                PebbleList([PebbleList([Symbol("a"), Symbol("b")]), "list"]),
                PebbleList([Symbol("_"), "string"])
            ]),
            env
        )
        assert result == "string"


class TestMatchLiteralElement:
    """Test literal elements in list patterns are enforced."""

    def test_match_literal_element_matches(self):
        """Test (match (list 1 2) ((1 x) x) (_ "no")) -> 2."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 1, 2]),
                PebbleList([
                    PebbleList([1, Symbol("x")]),
                    Symbol("x")
                ]),
                PebbleList([Symbol("_"), "no"])
            ]),
            env
        )
        assert result == 2

    def test_match_literal_element_fails(self):
        """Test (match (list 9 2) ((1 x) x) (_ "no")) -> "no"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 9, 2]),
                PebbleList([
                    PebbleList([1, Symbol("x")]),
                    Symbol("x")
                ]),
                PebbleList([Symbol("_"), "no"])
            ]),
            env
        )
        assert result == "no"


class TestMatchTaggedDispatch:
    """Test tagged dispatch with quoted-symbol tags."""

    def test_match_tagged_add(self):
        """Test dispatching on 'add tag: (match (list (quote add) 3 4) ...) -> 7."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), PebbleList([Symbol("quote"), Symbol("add")]), 3, 4]),
                PebbleList([
                    PebbleList([
                        PebbleList([Symbol("quote"), Symbol("add")]),
                        Symbol("x"),
                        Symbol("y")
                    ]),
                    PebbleList([Symbol("+"), Symbol("x"), Symbol("y")])
                ]),
                PebbleList([
                    PebbleList([
                        PebbleList([Symbol("quote"), Symbol("sub")]),
                        Symbol("x"),
                        Symbol("y")
                    ]),
                    PebbleList([Symbol("-"), Symbol("x"), Symbol("y")])
                ]),
                PebbleList([Symbol("_"), 0])
            ]),
            env
        )
        assert result == 7

    def test_match_tagged_sub(self):
        """Test dispatching on 'sub tag: (match (list (quote sub) 10 4) ...) -> 6."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), PebbleList([Symbol("quote"), Symbol("sub")]), 10, 4]),
                PebbleList([
                    PebbleList([
                        PebbleList([Symbol("quote"), Symbol("add")]),
                        Symbol("x"),
                        Symbol("y")
                    ]),
                    PebbleList([Symbol("+"), Symbol("x"), Symbol("y")])
                ]),
                PebbleList([
                    PebbleList([
                        PebbleList([Symbol("quote"), Symbol("sub")]),
                        Symbol("x"),
                        Symbol("y")
                    ]),
                    PebbleList([Symbol("-"), Symbol("x"), Symbol("y")])
                ]),
                PebbleList([Symbol("_"), 0])
            ]),
            env
        )
        assert result == 6

    def test_match_tagged_wrong_tag_fallthrough(self):
        """Test that wrong tag falls through: (match (list (quote mul) 3 4) ...) -> "no-match"."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), PebbleList([Symbol("quote"), Symbol("mul")]), 3, 4]),
                PebbleList([
                    PebbleList([
                        PebbleList([Symbol("quote"), Symbol("add")]),
                        Symbol("x"),
                        Symbol("y")
                    ]),
                    PebbleList([Symbol("+"), Symbol("x"), Symbol("y")])
                ]),
                PebbleList([Symbol("_"), "no-match"])
            ]),
            env
        )
        assert result == "no-match"


class TestMatchTailPattern:
    """Test tail pattern matching."""

    def test_match_tail_pattern_basic(self):
        """Test (match (list 1 2 3 4) ((first . rest) rest)) -> (2 3 4)."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 1, 2, 3, 4]),
                PebbleList([
                    PebbleList([Symbol("first"), Symbol("."), Symbol("rest")]),
                    Symbol("rest")
                ])
            ]),
            env
        )
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == 2
        assert result[1] == 3
        assert result[2] == 4

    def test_match_tail_pattern_empty(self):
        """Test (match (list 1) ((x . rest) rest)) -> nil."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), 1]),
                PebbleList([
                    PebbleList([Symbol("x"), Symbol("."), Symbol("rest")]),
                    Symbol("rest")
                ])
            ]),
            env
        )
        assert result == NIL

    def test_match_tail_pattern_with_quoted_symbol_head(self):
        """Test tail with quoted-symbol head: (match (list (quote cons) 1 2 3) (((quote cons) . rest) rest))."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("match"),
                PebbleList([Symbol("list"), PebbleList([Symbol("quote"), Symbol("cons")]), 1, 2, 3]),
                PebbleList([
                    PebbleList([
                        PebbleList([Symbol("quote"), Symbol("cons")]),
                        Symbol("."),
                        Symbol("rest")
                    ]),
                    Symbol("rest")
                ])
            ]),
            env
        )
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 3
