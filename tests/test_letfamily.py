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


class TestIfLet:
    """Tests for if-let binding macro."""

    def test_if_let_truthy_uses_then_branch(self):
        """if-let with truthy value should evaluate THEN branch with VAR in scope."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = "(if-let (x 5) (* x 2) 0)"
        result = eval_source(source, env)
        assert result == 10

    def test_if_let_falsy_false_uses_else_branch(self):
        """if-let with false should evaluate ELSE branch."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = "(if-let (x false) (* x 2) 99)"
        result = eval_source(source, env)
        assert result == 99

    def test_if_let_falsy_nil_uses_else_branch(self):
        """if-let with nil should evaluate ELSE branch."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = '(if-let (x nil) "yes" "no")'
        result = eval_source(source, env)
        assert result == "no"

    def test_if_let_no_else_falsy_returns_nil(self):
        """if-let without ELSE, when false, returns nil."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = "(if-let (x false) 1)"
        result = eval_source(source, env)
        assert result == NIL

    def test_if_let_zero_is_truthy(self):
        """Pebble truthiness: 0 is truthy, not falsy."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = '(if-let (x 0) "truthy" "falsy")'
        result = eval_source(source, env)
        assert result == "truthy"

    def test_if_let_empty_string_is_truthy(self):
        """Pebble truthiness: empty string is truthy, not falsy."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = '(if-let (x "") "t" "f")'
        result = eval_source(source, env)
        assert result == "t"

    def test_if_let_var_in_scope_then_branch(self):
        """VAR should be bound and available in THEN branch."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = "(if-let (x 5) (+ x 10) 0)"
        result = eval_source(source, env)
        assert result == 15

    def test_if_let_single_evaluation_of_expr(self):
        """EXPR should be evaluated exactly once, checking via side effect."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = """
        (define counter 0)
        (if-let (x (begin (set! counter (+ counter 1)) 5))
          counter
          0)
        """
        result = eval_source(source, env)
        # counter should be 1 after one if-let with truthy result
        assert result == 1

    def test_if_let_single_evaluation_falsy_case(self):
        """EXPR should be evaluated exactly once even in falsy case."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = """
        (define counter 0)
        (if-let (x (begin (set! counter (+ counter 1)) false))
          "yes"
          counter)
        """
        result = eval_source(source, env)
        # counter should be 1 after if-let evaluation
        assert result == 1


class TestWhenLet:
    """Tests for when-let binding macro."""

    def test_when_let_truthy_returns_body_value(self):
        """when-let with truthy value should evaluate body and return last form's value."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = "(when-let (x 5) (* x x))"
        result = eval_source(source, env)
        assert result == 25

    def test_when_let_falsy_returns_nil(self):
        """when-let with falsy value should return nil."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = "(when-let (x false) (* x x))"
        result = eval_source(source, env)
        assert result == NIL

    def test_when_let_falsy_body_does_not_run(self):
        """when-let with falsy value should NOT execute body (verify via side effect)."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = """
        (define counter 0)
        (when-let (x false)
          (set! counter (+ counter 1)))
        counter
        """
        result = eval_source(source, env)
        # counter should still be 0 because body did not run
        assert result == 0

    def test_when_let_multi_form_body_returns_last(self):
        """when-let with multiple body forms should return the last form's value."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = """
        (define counter 0)
        (when-let (x 5)
          (set! counter (+ counter 1))
          (set! counter (+ counter 10))
          counter)
        """
        result = eval_source(source, env)
        # should return the final value of counter (11), and counter should have been modified
        assert result == 11

    def test_when_let_zero_is_truthy(self):
        """Pebble truthiness: 0 is truthy in when-let."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = '(when-let (x 0) "ran")'
        result = eval_source(source, env)
        assert result == "ran"

    def test_when_let_var_in_scope(self):
        """VAR should be bound and available in body."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = "(when-let (x 5) (+ x 3))"
        result = eval_source(source, env)
        assert result == 8

    def test_when_let_single_evaluation_of_expr(self):
        """EXPR should be evaluated exactly once, checking via side effect."""
        env = make_global_env()
        from pebble.evaluator import eval_source
        source = """
        (define counter 0)
        (when-let (x (begin (set! counter (+ counter 1)) 5))
          (+ counter x))
        """
        result = eval_source(source, env)
        # counter incremented once, then we add counter (1) + x (5) = 6
        assert result == 6
