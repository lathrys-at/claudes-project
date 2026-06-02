"""Tests for the Collatz sequence example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


@pytest.fixture(scope="module")
def collatz_env_and_output():
    """Load the collatz.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "collatz.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestCollatz:
    """Tests for the Collatz sequence."""

    def test_example_output(self, collatz_env_and_output):
        """Test that the example file produces the correct output."""
        env, demo_output = collatz_env_and_output

        # The demo should print the Collatz sequence for 6
        expected_output = "(6 3 10 5 16 8 4 2 1)\n"
        assert demo_output == expected_output

    def test_collatz_1(self, collatz_env_and_output):
        """Test collatz(1) = (1)."""
        env, _ = collatz_env_and_output
        result = eval_source("(collatz 1)", env)

        assert isinstance(result, PebbleList)
        assert list(result) == [1]

    def test_collatz_2(self, collatz_env_and_output):
        """Test collatz(2) = (2 1)."""
        env, _ = collatz_env_and_output
        result = eval_source("(collatz 2)", env)

        assert isinstance(result, PebbleList)
        assert list(result) == [2, 1]

    def test_collatz_3(self, collatz_env_and_output):
        """Test collatz(3) = (3 10 5 16 8 4 2 1)."""
        env, _ = collatz_env_and_output
        result = eval_source("(collatz 3)", env)

        expected = [3, 10, 5, 16, 8, 4, 2, 1]
        assert list(result) == expected

    def test_collatz_6(self, collatz_env_and_output):
        """Test collatz(6) = (6 3 10 5 16 8 4 2 1)."""
        env, _ = collatz_env_and_output
        result = eval_source("(collatz 6)", env)

        expected = [6, 3, 10, 5, 16, 8, 4, 2, 1]
        assert list(result) == expected

    def test_collatz_7(self, collatz_env_and_output):
        """Test collatz(7) = (7 22 11 34 17 52 26 13 40 20 10 5 16 8 4 2 1)."""
        env, _ = collatz_env_and_output
        result = eval_source("(collatz 7)", env)

        expected = [7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]
        assert list(result) == expected

    def test_collatz_length_1(self, collatz_env_and_output):
        """Test collatz-length(1) = 1."""
        env, _ = collatz_env_and_output
        result = eval_source("(collatz-length 1)", env)
        assert result == 1

    def test_collatz_length_6(self, collatz_env_and_output):
        """Test collatz-length(6) = 9."""
        env, _ = collatz_env_and_output
        result = eval_source("(collatz-length 6)", env)
        assert result == 9

    def test_collatz_length_7(self, collatz_env_and_output):
        """Test collatz-length(7) = 17."""
        env, _ = collatz_env_and_output
        result = eval_source("(collatz-length 7)", env)
        assert result == 17

    def test_collatz_length_27(self, collatz_env_and_output):
        """Test collatz-length(27) = 112 (stack-safety check for long sequences)."""
        env, _ = collatz_env_and_output
        result = eval_source("(collatz-length 27)", env)
        assert result == 112

    def test_collatz_error_zero(self, collatz_env_and_output):
        """Test that collatz(0) raises an EvalError."""
        env, _ = collatz_env_and_output

        with pytest.raises(Exception) as exc_info:
            eval_source("(collatz 0)", env)
        assert "collatz: n must be >= 1" in str(exc_info.value)

    def test_collatz_error_negative(self, collatz_env_and_output):
        """Test that collatz(-5) raises an EvalError."""
        env, _ = collatz_env_and_output

        with pytest.raises(Exception) as exc_info:
            eval_source("(collatz -5)", env)
        assert "collatz: n must be >= 1" in str(exc_info.value)

    def test_collatz_error_non_integer(self, collatz_env_and_output):
        """Test that collatz with a non-integer raises an EvalError."""
        env, _ = collatz_env_and_output

        with pytest.raises(Exception) as exc_info:
            eval_source("(collatz 3.5)", env)
        assert "collatz: n must be an integer" in str(exc_info.value)
