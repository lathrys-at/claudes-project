"""Tests for the symbolic algebra simplifier example."""
import pytest
from io import StringIO
import sys
from pathlib import Path

from pebble.evaluator import make_global_env, seval
from pebble.reader import read
from pebble.types import Symbol, PebbleList, NIL


class TestSimplifyProgram:
    """Test that the simplify.pebble example loads and runs correctly."""

    @pytest.fixture
    def simplify_env(self):
        """Load the simplify.pebble program and return the environment."""
        env = make_global_env()

        # Load the simplify.pebble file
        simplify_path = Path(__file__).parent.parent / "examples" / "simplify.pebble"
        with open(simplify_path) as f:
            code = f.read()

        # Read and evaluate all forms in the file
        forms = read(code)
        for form in forms:
            seval(form, env)

        return env

    def test_simplify_demo_output(self):
        """Test that running the program produces the exact expected output."""
        env = make_global_env()

        # Load the simplify.pebble file
        simplify_path = Path(__file__).parent.parent / "examples" / "simplify.pebble"
        with open(simplify_path) as f:
            code = f.read()

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            forms = read(code)
            for form in forms:
                seval(form, env)

            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        # Check the output lines
        lines = output.strip().split('\n')
        assert len(lines) == 4, f"Expected 4 output lines, got {len(lines)}: {lines}"
        assert lines[0] == 'x', f"Line 1: expected 'x', got '{lines[0]}'"
        assert lines[1] == '0', f"Line 2: expected '0', got '{lines[1]}'"
        assert lines[2] == '(* x y)', f"Line 3: expected '(* x y)', got '{lines[2]}'"
        assert lines[3] == '6', f"Line 4: expected '6', got '{lines[3]}'"

    def test_simplify_addition_identity_right(self, simplify_env):
        """Test: (simplify (quote (+ x 0))) -> x"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("+"), Symbol("x"), 0])
                ])
            ]),
            simplify_env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_addition_identity_left(self, simplify_env):
        """Test: (simplify (quote (+ 0 x))) -> x"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("+"), 0, Symbol("x")])
                ])
            ]),
            simplify_env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_multiplication_identity_right(self, simplify_env):
        """Test: (simplify (quote (* x 1))) -> x"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("*"), Symbol("x"), 1])
                ])
            ]),
            simplify_env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_multiplication_identity_left(self, simplify_env):
        """Test: (simplify (quote (* 1 x))) -> x"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("*"), 1, Symbol("x")])
                ])
            ]),
            simplify_env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_multiplication_zero_left(self, simplify_env):
        """Test: (simplify (quote (* x 0))) -> 0"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("*"), Symbol("x"), 0])
                ])
            ]),
            simplify_env
        )
        assert result == 0, f"Expected 0, got {result}"

    def test_simplify_multiplication_zero_right(self, simplify_env):
        """Test: (simplify (quote (* 0 x))) -> 0"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("*"), 0, Symbol("x")])
                ])
            ]),
            simplify_env
        )
        assert result == 0, f"Expected 0, got {result}"

    def test_simplify_subtraction_zero(self, simplify_env):
        """Test: (simplify (quote (- x 0))) -> x"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("-"), Symbol("x"), 0])
                ])
            ]),
            simplify_env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_constant_fold_addition(self, simplify_env):
        """Test: (simplify (quote (+ 2 3))) -> 5"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([Symbol("+"), 2, 3])
            ]),
            simplify_env
        )
        assert result == 5, f"Expected 5, got {result}"

    def test_simplify_constant_fold_multiplication(self, simplify_env):
        """Test: (simplify (quote (* 2 3))) -> 6"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([Symbol("*"), 2, 3])
            ]),
            simplify_env
        )
        assert result == 6, f"Expected 6, got {result}"

    def test_simplify_constant_fold_subtraction(self, simplify_env):
        """Test: (simplify (quote (- 5 2))) -> 3"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([Symbol("-"), 5, 2])
            ]),
            simplify_env
        )
        assert result == 3, f"Expected 3, got {result}"

    def test_simplify_symbol_atom(self, simplify_env):
        """Test: (simplify (quote x)) -> x"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([Symbol("quote"), Symbol("x")])
            ]),
            simplify_env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_number_atom(self, simplify_env):
        """Test: (simplify 5) -> 5"""
        result = seval(
            PebbleList([Symbol("simplify"), 5]),
            simplify_env
        )
        assert result == 5, f"Expected 5, got {result}"

    def test_simplify_nested_addition_multiplication(self, simplify_env):
        """Test nested: (simplify (quote (+ (* x 1) 0))) -> x"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([
                        Symbol("+"),
                        PebbleList([Symbol("*"), Symbol("x"), 1]),
                        0
                    ])
                ])
            ]),
            simplify_env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_nested_multiple(self, simplify_env):
        """Test nested: (simplify (quote (* (+ x 0) (+ y 0)))) -> (* x y)"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([
                        Symbol("*"),
                        PebbleList([Symbol("+"), Symbol("x"), 0]),
                        PebbleList([Symbol("+"), Symbol("y"), 0])
                    ])
                ])
            ]),
            simplify_env
        )
        expected = PebbleList([Symbol("*"), Symbol("x"), Symbol("y")])
        assert result == expected, f"Expected {expected}, got {result}"

    def test_simplify_nested_with_constant_folding(self, simplify_env):
        """Test nested with folding: (simplify (quote (+ (* 2 3) (* x 0)))) -> 6"""
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([
                        Symbol("+"),
                        PebbleList([Symbol("*"), 2, 3]),
                        PebbleList([Symbol("*"), Symbol("x"), 0])
                    ])
                ])
            ]),
            simplify_env
        )
        assert result == 6, f"Expected 6, got {result}"
