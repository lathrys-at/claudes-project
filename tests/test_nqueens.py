"""Tests for the N-Queens example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


@pytest.fixture(scope="module")
def nqueens_env_and_output():
    """Load the nqueens.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "nqueens.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestNQueens:
    """Tests for the N-Queens solution counter."""

    def test_example_output(self, nqueens_env_and_output):
        """Test that the example file produces the correct output (92 for n=8)."""
        env, demo_output = nqueens_env_and_output
        assert demo_output.strip() == "92"

    def test_nqueens_1(self, nqueens_env_and_output):
        """Test n-queens for n=1."""
        env, _ = nqueens_env_and_output
        result = eval_source("(n-queens 1)", env)
        assert result == 1

    def test_nqueens_2(self, nqueens_env_and_output):
        """Test n-queens for n=2 (no solutions)."""
        env, _ = nqueens_env_and_output
        result = eval_source("(n-queens 2)", env)
        assert result == 0

    def test_nqueens_3(self, nqueens_env_and_output):
        """Test n-queens for n=3 (no solutions)."""
        env, _ = nqueens_env_and_output
        result = eval_source("(n-queens 3)", env)
        assert result == 0

    def test_nqueens_4(self, nqueens_env_and_output):
        """Test n-queens for n=4."""
        env, _ = nqueens_env_and_output
        result = eval_source("(n-queens 4)", env)
        assert result == 2

    def test_nqueens_5(self, nqueens_env_and_output):
        """Test n-queens for n=5."""
        env, _ = nqueens_env_and_output
        result = eval_source("(n-queens 5)", env)
        assert result == 10

    def test_nqueens_6(self, nqueens_env_and_output):
        """Test n-queens for n=6."""
        env, _ = nqueens_env_and_output
        result = eval_source("(n-queens 6)", env)
        assert result == 4

    def test_nqueens_7(self, nqueens_env_and_output):
        """Test n-queens for n=7."""
        env, _ = nqueens_env_and_output
        result = eval_source("(n-queens 7)", env)
        assert result == 40

    def test_nqueens_8(self, nqueens_env_and_output):
        """Test n-queens for n=8."""
        env, _ = nqueens_env_and_output
        result = eval_source("(n-queens 8)", env)
        assert result == 92

    def test_nqueens_error_zero(self, nqueens_env_and_output):
        """Test that n-queens raises EvalError for n=0."""
        env, _ = nqueens_env_and_output
        with pytest.raises(Exception) as excinfo:
            eval_source("(n-queens 0)", env)
        assert "must be >= 1" in str(excinfo.value)

    def test_nqueens_error_negative(self, nqueens_env_and_output):
        """Test that n-queens raises EvalError for negative n."""
        env, _ = nqueens_env_and_output
        with pytest.raises(Exception) as excinfo:
            eval_source("(n-queens -1)", env)
        assert "must be >= 1" in str(excinfo.value)

    def test_nqueens_error_not_integer(self, nqueens_env_and_output):
        """Test that n-queens raises EvalError for non-integer input."""
        env, _ = nqueens_env_and_output
        with pytest.raises(Exception) as excinfo:
            eval_source("(n-queens 3.5)", env)
        assert "must be an integer" in str(excinfo.value)
