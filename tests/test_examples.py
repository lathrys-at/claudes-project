"""Tests for example Pebble programs."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


def _load_example(filename):
    """Helper function to load an example file and capture its output."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / filename
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def fizzbuzz_env_and_output():
    """Load fizzbuzz.pebble once and capture its output."""
    return _load_example("fizzbuzz.pebble")


@pytest.fixture(scope="module")
def fibonacci_env_and_output():
    """Load fibonacci.pebble once and capture its output."""
    return _load_example("fibonacci.pebble")


@pytest.fixture(scope="module")
def quicksort_env_and_output():
    """Load quicksort.pebble once and capture its output."""
    return _load_example("quicksort.pebble")


@pytest.fixture(scope="module")
def wordcount_env_and_output():
    """Load wordcount.pebble once and capture its output."""
    return _load_example("wordcount.pebble")


@pytest.fixture(scope="module")
def error_handling_env_and_output():
    """Load error_handling.pebble once and capture its output."""
    return _load_example("error_handling.pebble")


class TestExamples:
    """Tests for the example programs in examples/ directory."""

    def test_fizzbuzz(self, fizzbuzz_env_and_output):
        """Test FizzBuzz example."""
        env, demo_output = fizzbuzz_env_and_output

        expected_lines = [
            "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz",
            "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_fibonacci(self, fibonacci_env_and_output):
        """Test Fibonacci example."""
        env, demo_output = fibonacci_env_and_output

        expected = "0 1 1 2 3 5 8 13 21 34"
        assert demo_output.strip() == expected

    def test_quicksort(self, quicksort_env_and_output):
        """Test Quicksort example."""
        env, demo_output = quicksort_env_and_output

        expected = "(1 2 3 4 6 8 9)"
        assert demo_output.strip() == expected

    def test_wordcount(self, wordcount_env_and_output):
        """Test Word count example."""
        env, demo_output = wordcount_env_and_output

        expected_lines = [
            "apple: 3",
            "banana: 2",
            "cherry: 1"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_error_handling(self, error_handling_env_and_output):
        """Test Error handling example."""
        env, demo_output = error_handling_env_and_output

        expected_lines = [
            "caught: something went wrong",
            "result: 30"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines
