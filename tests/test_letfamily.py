"""Tests for letrec and named let special forms."""
import pytest
from pebble.evaluator import make_global_env, seval, EvalError
from pebble.types import Symbol, PebbleList, NIL


class TestLetrec:
    """Tests for letrec special form."""

    def test_single_recursion(self):
        """Test factorial using letrec."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("letrec"),
                PebbleList([
                    PebbleList([
                        Symbol("fact"),
                        PebbleList([
                            Symbol("lambda"),
                            PebbleList([Symbol("n")]),
                            PebbleList([
                                Symbol("if"),
                                PebbleList([Symbol("="), Symbol("n"), 0]),
                                1,
                                PebbleList([
                                    Symbol("*"),
                                    Symbol("n"),
                                    PebbleList([Symbol("fact"), PebbleList([Symbol("-"), Symbol("n"), 1])])
                                ])
                            ])
                        ])
                    ])
                ]),
                PebbleList([Symbol("fact"), 5])
            ]),
            env
        )
        assert result == 120

    def test_mutual_recursion_even(self):
        """Test mutual recursion: even? and odd?"""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("letrec"),
                PebbleList([
                    PebbleList([
                        Symbol("my-even?"),
                        PebbleList([
                            Symbol("lambda"),
                            PebbleList([Symbol("n")]),
                            PebbleList([
                                Symbol("if"),
                                PebbleList([Symbol("="), Symbol("n"), 0]),
                                True,
                                PebbleList([Symbol("my-odd?"), PebbleList([Symbol("-"), Symbol("n"), 1])])
                            ])
                        ])
                    ]),
                    PebbleList([
                        Symbol("my-odd?"),
                        PebbleList([
                            Symbol("lambda"),
                            PebbleList([Symbol("n")]),
                            PebbleList([
                                Symbol("if"),
                                PebbleList([Symbol("="), Symbol("n"), 0]),
                                False,
                                PebbleList([Symbol("my-even?"), PebbleList([Symbol("-"), Symbol("n"), 1])])
                            ])
                        ])
                    ])
                ]),
                PebbleList([Symbol("my-even?"), 10])
            ]),
            env
        )
        assert result is True

    def test_mutual_recursion_odd(self):
        """Test mutual recursion: odd case."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("letrec"),
                PebbleList([
                    PebbleList([
                        Symbol("my-even?"),
                        PebbleList([
                            Symbol("lambda"),
                            PebbleList([Symbol("n")]),
                            PebbleList([
                                Symbol("if"),
                                PebbleList([Symbol("="), Symbol("n"), 0]),
                                True,
                                PebbleList([Symbol("my-odd?"), PebbleList([Symbol("-"), Symbol("n"), 1])])
                            ])
                        ])
                    ]),
                    PebbleList([
                        Symbol("my-odd?"),
                        PebbleList([
                            Symbol("lambda"),
                            PebbleList([Symbol("n")]),
                            PebbleList([
                                Symbol("if"),
                                PebbleList([Symbol("="), Symbol("n"), 0]),
                                False,
                                PebbleList([Symbol("my-even?"), PebbleList([Symbol("-"), Symbol("n"), 1])])
                            ])
                        ])
                    ])
                ]),
                PebbleList([Symbol("my-even?"), 7])
            ]),
            env
        )
        assert result is False

    def test_body_returns_last_form(self):
        """Test that letrec body returns the last form."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("letrec"),
                PebbleList([
                    PebbleList([Symbol("x"), 42])
                ]),
                1,
                2,
                3
            ]),
            env
        )
        assert result == 3

    def test_body_sees_bindings(self):
        """Test that body can access the bound variables."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("letrec"),
                PebbleList([
                    PebbleList([Symbol("x"), 10]),
                    PebbleList([Symbol("y"), 20])
                ]),
                PebbleList([Symbol("+"), Symbol("x"), Symbol("y")])
            ]),
            env
        )
        assert result == 30

    def test_tail_call_optimization(self):
        """Test that tail recursion in letrec-bound function doesn't overflow."""
        env = make_global_env()
        # Tail-recursive sum from 0 to 5000
        result = seval(
            PebbleList([
                Symbol("letrec"),
                PebbleList([
                    PebbleList([
                        Symbol("sum-to"),
                        PebbleList([
                            Symbol("lambda"),
                            PebbleList([Symbol("n"), Symbol("acc")]),
                            PebbleList([
                                Symbol("if"),
                                PebbleList([Symbol("="), Symbol("n"), 0]),
                                Symbol("acc"),
                                PebbleList([
                                    Symbol("sum-to"),
                                    PebbleList([Symbol("-"), Symbol("n"), 1]),
                                    PebbleList([Symbol("+"), Symbol("acc"), Symbol("n")])
                                ])
                            ])
                        ])
                    ])
                ]),
                PebbleList([Symbol("sum-to"), 5000, 0])
            ]),
            env
        )
        # sum(1..5000) = 5000*5001/2 = 12502500
        assert result == 12502500

    def test_malformed_bindings_not_list(self):
        """Test that non-list bindings raise EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            seval(
                PebbleList([
                    Symbol("letrec"),
                    42,  # Not a list
                    Symbol("x")
                ]),
                env
            )

    def test_malformed_binding_not_pair(self):
        """Test that binding that's not a pair raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            seval(
                PebbleList([
                    Symbol("letrec"),
                    PebbleList([
                        PebbleList([Symbol("x")])  # Only one element
                    ]),
                    Symbol("x")
                ]),
                env
            )

    def test_malformed_binding_name_not_symbol(self):
        """Test that non-symbol binding name raises EvalError."""
        env = make_global_env()
        with pytest.raises(EvalError):
            seval(
                PebbleList([
                    Symbol("letrec"),
                    PebbleList([
                        PebbleList([42, 10])  # 42 is not a symbol
                    ]),
                    10
                ]),
                env
            )


class TestNamedLet:
    """Tests for named let special form."""

    def test_summation_loop(self):
        """Test summation using named let."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("let"),
                Symbol("loop"),
                PebbleList([
                    PebbleList([Symbol("i"), 0]),
                    PebbleList([Symbol("acc"), 0])
                ]),
                PebbleList([
                    Symbol("if"),
                    PebbleList([Symbol("="), Symbol("i"), 5]),
                    Symbol("acc"),
                    PebbleList([
                        Symbol("loop"),
                        PebbleList([Symbol("+"), Symbol("i"), 1]),
                        PebbleList([Symbol("+"), Symbol("acc"), Symbol("i")])
                    ])
                ])
            ]),
            env
        )
        assert result == 10

    def test_factorial_via_named_let(self):
        """Test factorial using named let with accumulator."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("let"),
                Symbol("fact"),
                PebbleList([
                    PebbleList([Symbol("n"), 5]),
                    PebbleList([Symbol("acc"), 1])
                ]),
                PebbleList([
                    Symbol("if"),
                    PebbleList([Symbol("="), Symbol("n"), 0]),
                    Symbol("acc"),
                    PebbleList([
                        Symbol("fact"),
                        PebbleList([Symbol("-"), Symbol("n"), 1]),
                        PebbleList([Symbol("*"), Symbol("n"), Symbol("acc")])
                    ])
                ])
            ]),
            env
        )
        assert result == 120

    def test_tail_call_optimization(self):
        """Test that tail recursion in named let doesn't overflow."""
        env = make_global_env()
        # Tail-recursive sum from 0 to 5000
        result = seval(
            PebbleList([
                Symbol("let"),
                Symbol("sum-to"),
                PebbleList([
                    PebbleList([Symbol("n"), 5000]),
                    PebbleList([Symbol("acc"), 0])
                ]),
                PebbleList([
                    Symbol("if"),
                    PebbleList([Symbol("="), Symbol("n"), 0]),
                    Symbol("acc"),
                    PebbleList([
                        Symbol("sum-to"),
                        PebbleList([Symbol("-"), Symbol("n"), 1]),
                        PebbleList([Symbol("+"), Symbol("acc"), Symbol("n")])
                    ])
                ])
            ]),
            env
        )
        # sum(1..5000) = 5000*5001/2 = 12502500
        assert result == 12502500

    def test_ordinary_let_still_works(self):
        """Test that ordinary let (bindings as first element) still works."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("let"),
                PebbleList([
                    PebbleList([Symbol("x"), 1]),
                    PebbleList([Symbol("y"), 2])
                ]),
                PebbleList([Symbol("+"), Symbol("x"), Symbol("y")])
            ]),
            env
        )
        assert result == 3

    def test_ordinary_let_multi_body(self):
        """Test that ordinary let with multiple body forms still works."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("let"),
                PebbleList([
                    PebbleList([Symbol("x"), 5])
                ]),
                PebbleList([Symbol("*"), Symbol("x"), 2]),  # Ignored
                PebbleList([Symbol("+"), Symbol("x"), 3])   # Returned
            ]),
            env
        )
        assert result == 8

    def test_named_let_with_no_bindings(self):
        """Test named let with an empty bindings list."""
        env = make_global_env()
        result = seval(
            PebbleList([
                Symbol("let"),
                Symbol("loop"),
                PebbleList([]),
                42
            ]),
            env
        )
        assert result == 42
