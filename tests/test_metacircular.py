"""Tests for the meta-circular evaluator example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList


class TestMetacircular:
    """Tests for the meta-circular Lisp evaluator."""

    def test_example_output(self, capsys):
        """Test that the example file produces the correct output."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        captured = capsys.readouterr()
        expected_lines = [
            "(* 2 (+ 3 4)) = 14",
            "fact(5) = 120",
            "fib(10) = 55"
        ]
        output_lines = captured.out.strip().split('\n')
        assert output_lines == expected_lines

    def test_mc_eval_number(self):
        """Test that mc-eval evaluates numbers correctly."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        # Evaluate: (mc-eval 42 nil (base-env))
        result = eval_source("(mc-eval 42 nil (base-env))", env)
        assert result == 42

    def test_mc_run_simple_arithmetic(self):
        """Test mc-run with simple arithmetic."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        result = eval_source("(mc-run (quote ((+ 1 2))))", env)
        assert result == 3

    def test_mc_run_nested_arithmetic(self):
        """Test mc-run with nested arithmetic: (* 2 (+ 3 4)) -> 14."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        result = eval_source("(mc-run (quote ((* 2 (+ 3 4)))))", env)
        assert result == 14

    def test_mc_run_if_true(self):
        """Test mc-run with if condition that is true."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        result = eval_source("(mc-run (quote ((if (< 1 2) 10 20))))", env)
        assert result == 10

    def test_mc_run_if_false(self):
        """Test mc-run with if condition that is false."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        result = eval_source("(mc-run (quote ((if (> 1 2) 10 20))))", env)
        assert result == 20

    def test_mc_run_lambda_application(self):
        """Test mc-run with lambda application: ((lambda (x) (* x x)) 5) -> 25."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        result = eval_source("(mc-run (quote (((lambda (x) (* x x)) 5))))", env)
        assert result == 25

    def test_mc_run_quote(self):
        """Test mc-run with quote: (quote (1 2 3)) -> (1 2 3)."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        result = eval_source("(mc-run (quote ((quote (1 2 3)))))", env)
        # Should be a PebbleList with elements 1, 2, 3
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 3

    def test_mc_run_lexical_closure(self):
        """Test lexical closures: make-adder creates an adder function."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        # (mc-run '((define make-adder (lambda (n) (lambda (x) (+ x n))))
        #            ((make-adder 3) 4)))
        result = eval_source(
            "(mc-run (quote ((define make-adder (lambda (n) (lambda (x) (+ x n)))) ((make-adder 3) 4))))",
            env
        )
        assert result == 7

    def test_mc_run_recursion_factorial(self):
        """Test recursion: factorial of 5 should be 120."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        # (mc-run '((define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))
        #            (fact 5)))
        result = eval_source(
            "(mc-run (quote ((define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1)))))) (fact 5))))",
            env
        )
        assert result == 120

    def test_mc_run_recursion_fibonacci(self):
        """Test recursion: fibonacci of 10 should be 55."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        # (mc-run '((define fib (lambda (n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2))))))
        #            (fib 10)))
        result = eval_source(
            "(mc-run (quote ((define fib (lambda (n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2)))))) (fib 10))))",
            env
        )
        assert result == 55

    def test_mc_run_multiple_definitions(self):
        """Test multiple top-level definitions: x=10, y=20, x+y=30."""
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        # (mc-run '((define x 10) (define y 20) (+ x y)))
        result = eval_source(
            "(mc-run (quote ((define x 10) (define y 20) (+ x y))))",
            env
        )
        assert result == 30
