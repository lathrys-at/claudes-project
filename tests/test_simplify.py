"""Tests for the symbolic algebra simplifier example."""
import pytest
from io import StringIO
import sys
from pathlib import Path

from pebble.evaluator import make_global_env, seval
from pebble.reader import read
from pebble.types import Symbol, PebbleList, NIL


def _load_simplify_example():
    """Helper function to load simplify.pebble and capture its output."""
    env = make_global_env()

    # Load the simplify.pebble file
    simplify_path = Path(__file__).parent.parent / "examples" / "simplify.pebble"
    with open(simplify_path) as f:
        code = f.read()

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        # Read and evaluate all forms in the file
        forms = read(code)
        for form in forms:
            seval(form, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def simplify_env_and_output():
    """Load simplify.pebble once and capture its output."""
    return _load_simplify_example()


class TestSimplifyProgram:
    """Test that the simplify.pebble example loads and runs correctly."""

    def test_simplify_demo_output(self, simplify_env_and_output):
        """Test that running the program produces the exact expected output."""
        env, demo_output = simplify_env_and_output

        # Check the output lines
        lines = demo_output.strip().split('\n')
        assert len(lines) == 4, f"Expected 4 output lines, got {len(lines)}: {lines}"
        assert lines[0] == 'x', f"Line 1: expected 'x', got '{lines[0]}'"
        assert lines[1] == '0', f"Line 2: expected '0', got '{lines[1]}'"
        assert lines[2] == '(* x y)', f"Line 3: expected '(* x y)', got '{lines[2]}'"
        assert lines[3] == '6', f"Line 4: expected '6', got '{lines[3]}'"

    def test_simplify_addition_identity_right(self, simplify_env_and_output):
        """Test: (simplify (quote (+ x 0))) -> x"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("+"), Symbol("x"), 0])
                ])
            ]),
            env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_addition_identity_left(self, simplify_env_and_output):
        """Test: (simplify (quote (+ 0 x))) -> x"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("+"), 0, Symbol("x")])
                ])
            ]),
            env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_multiplication_identity_right(self, simplify_env_and_output):
        """Test: (simplify (quote (* x 1))) -> x"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("*"), Symbol("x"), 1])
                ])
            ]),
            env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_multiplication_identity_left(self, simplify_env_and_output):
        """Test: (simplify (quote (* 1 x))) -> x"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("*"), 1, Symbol("x")])
                ])
            ]),
            env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_multiplication_zero_left(self, simplify_env_and_output):
        """Test: (simplify (quote (* x 0))) -> 0"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("*"), Symbol("x"), 0])
                ])
            ]),
            env
        )
        assert result == 0, f"Expected 0, got {result}"

    def test_simplify_multiplication_zero_right(self, simplify_env_and_output):
        """Test: (simplify (quote (* 0 x))) -> 0"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("*"), 0, Symbol("x")])
                ])
            ]),
            env
        )
        assert result == 0, f"Expected 0, got {result}"

    def test_simplify_subtraction_zero(self, simplify_env_and_output):
        """Test: (simplify (quote (- x 0))) -> x"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([
                    Symbol("quote"),
                    PebbleList([Symbol("-"), Symbol("x"), 0])
                ])
            ]),
            env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_constant_fold_addition(self, simplify_env_and_output):
        """Test: (simplify (quote (+ 2 3))) -> 5"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([Symbol("+"), 2, 3])
            ]),
            env
        )
        assert result == 5, f"Expected 5, got {result}"

    def test_simplify_constant_fold_multiplication(self, simplify_env_and_output):
        """Test: (simplify (quote (* 2 3))) -> 6"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([Symbol("*"), 2, 3])
            ]),
            env
        )
        assert result == 6, f"Expected 6, got {result}"

    def test_simplify_constant_fold_subtraction(self, simplify_env_and_output):
        """Test: (simplify (quote (- 5 2))) -> 3"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([Symbol("-"), 5, 2])
            ]),
            env
        )
        assert result == 3, f"Expected 3, got {result}"

    def test_simplify_symbol_atom(self, simplify_env_and_output):
        """Test: (simplify (quote x)) -> x"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([
                Symbol("simplify"),
                PebbleList([Symbol("quote"), Symbol("x")])
            ]),
            env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_number_atom(self, simplify_env_and_output):
        """Test: (simplify 5) -> 5"""
        env, _ = simplify_env_and_output
        result = seval(
            PebbleList([Symbol("simplify"), 5]),
            env
        )
        assert result == 5, f"Expected 5, got {result}"

    def test_simplify_nested_addition_multiplication(self, simplify_env_and_output):
        """Test nested: (simplify (quote (+ (* x 1) 0))) -> x"""
        env, _ = simplify_env_and_output
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
            env
        )
        assert result == Symbol("x"), f"Expected x, got {result}"

    def test_simplify_nested_multiple(self, simplify_env_and_output):
        """Test nested: (simplify (quote (* (+ x 0) (+ y 0)))) -> (* x y)"""
        env, _ = simplify_env_and_output
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
            env
        )
        expected = PebbleList([Symbol("*"), Symbol("x"), Symbol("y")])
        assert result == expected, f"Expected {expected}, got {result}"

    def test_simplify_nested_with_constant_folding(self, simplify_env_and_output):
        """Test nested with folding: (simplify (quote (+ (* 2 3) (* x 0)))) -> 6"""
        env, _ = simplify_env_and_output
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
            env
        )
        assert result == 6, f"Expected 6, got {result}"
