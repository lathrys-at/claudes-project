"""Tests for the meta-circular evaluator example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


@pytest.fixture(scope="module")
def metacircular_env_and_output():
    """Load the metacircular.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "metacircular.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestMetacircular:
    """Tests for the meta-circular Lisp evaluator."""

    def test_example_output(self, metacircular_env_and_output):
        """Test that the example file produces the correct output."""
        env, demo_output = metacircular_env_and_output

        expected_lines = [
            "(* 2 (+ 3 4)) = 14",
            "fact(5) = 120",
            "fib(10) = 55"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_mc_eval_number(self, metacircular_env_and_output):
        """Test that mc-eval evaluates numbers correctly."""
        env, _ = metacircular_env_and_output

        # Evaluate: (mc-eval 42 nil (base-env))
        result = eval_source("(mc-eval 42 nil (base-env))", env)
        assert result == 42

    def test_mc_run_simple_arithmetic(self, metacircular_env_and_output):
        """Test mc-run with simple arithmetic."""
        env, _ = metacircular_env_and_output

        result = eval_source("(mc-run (quote ((+ 1 2))))", env)
        assert result == 3

    def test_mc_run_nested_arithmetic(self, metacircular_env_and_output):
        """Test mc-run with nested arithmetic: (* 2 (+ 3 4)) -> 14."""
        env, _ = metacircular_env_and_output

        result = eval_source("(mc-run (quote ((* 2 (+ 3 4)))))", env)
        assert result == 14

    def test_mc_run_if_true(self, metacircular_env_and_output):
        """Test mc-run with if condition that is true."""
        env, _ = metacircular_env_and_output

        result = eval_source("(mc-run (quote ((if (< 1 2) 10 20))))", env)
        assert result == 10

    def test_mc_run_if_false(self, metacircular_env_and_output):
        """Test mc-run with if condition that is false."""
        env, _ = metacircular_env_and_output

        result = eval_source("(mc-run (quote ((if (> 1 2) 10 20))))", env)
        assert result == 20

    def test_mc_run_lambda_application(self, metacircular_env_and_output):
        """Test mc-run with lambda application: ((lambda (x) (* x x)) 5) -> 25."""
        env, _ = metacircular_env_and_output

        result = eval_source("(mc-run (quote (((lambda (x) (* x x)) 5))))", env)
        assert result == 25

    def test_mc_run_quote(self, metacircular_env_and_output):
        """Test mc-run with quote: (quote (1 2 3)) -> (1 2 3)."""
        env, _ = metacircular_env_and_output

        result = eval_source("(mc-run (quote ((quote (1 2 3)))))", env)
        # Should be a PebbleList with elements 1, 2, 3
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 3

    def test_mc_run_lexical_closure(self, metacircular_env_and_output):
        """Test lexical closures: make-adder creates an adder function."""
        env, _ = metacircular_env_and_output

        # (mc-run '((define make-adder (lambda (n) (lambda (x) (+ x n))))
        #            ((make-adder 3) 4)))
        result = eval_source(
            "(mc-run (quote ((define make-adder (lambda (n) (lambda (x) (+ x n)))) ((make-adder 3) 4))))",
            env
        )
        assert result == 7

    def test_mc_run_recursion_factorial(self, metacircular_env_and_output):
        """Test recursion: factorial of 5 should be 120."""
        env, _ = metacircular_env_and_output

        # (mc-run '((define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))
        #            (fact 5)))
        result = eval_source(
            "(mc-run (quote ((define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1)))))) (fact 5))))",
            env
        )
        assert result == 120

    def test_mc_run_recursion_fibonacci(self, metacircular_env_and_output):
        """Test recursion: fibonacci of 10 should be 55."""
        env, _ = metacircular_env_and_output

        # (mc-run '((define fib (lambda (n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2))))))
        #            (fib 10)))
        result = eval_source(
            "(mc-run (quote ((define fib (lambda (n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2)))))) (fib 10))))",
            env
        )
        assert result == 55

    def test_mc_run_multiple_definitions(self, metacircular_env_and_output):
        """Test multiple top-level definitions: x=10, y=20, x+y=30."""
        env, _ = metacircular_env_and_output

        # (mc-run '((define x 10) (define y 20) (+ x y)))
        result = eval_source(
            "(mc-run (quote ((define x 10) (define y 20) (+ x y))))",
            env
        )
        assert result == 30
