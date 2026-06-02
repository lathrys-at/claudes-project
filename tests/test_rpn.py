"""Tests for RPN calculator example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


def _load_rpn_example():
    """Helper function to load rpn.pebble and capture its output."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "rpn.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def rpn_env_and_output():
    """Load rpn.pebble once and capture its output."""
    return _load_rpn_example()


class TestRPN:
    """Tests for the RPN calculator example."""

    def test_rpn_demo_output(self, rpn_env_and_output):
        """Test that the demo outputs exactly three lines."""
        env, demo_output = rpn_env_and_output

        expected_lines = ["7", "35", "-10"]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_rpn_simple_addition(self, rpn_env_and_output):
        """Test simple addition: 3 4 + = 7"""
        env, _ = rpn_env_and_output
        result = eval_source("(rpn \"3 4 +\")", env)
        assert result == 7

    def test_rpn_complex_arithmetic(self, rpn_env_and_output):
        """Test complex arithmetic: 3 4 + 5 * = 35"""
        env, _ = rpn_env_and_output
        result = eval_source("(rpn \"3 4 + 5 *\")", env)
        assert result == 35

    def test_rpn_subtraction(self, rpn_env_and_output):
        """Test subtraction: 10 2 - = 8"""
        env, _ = rpn_env_and_output
        result = eval_source("(rpn \"10 2 -\")", env)
        assert result == 8

    def test_rpn_subtraction_with_multiplication(self, rpn_env_and_output):
        """Test subtraction with multiplication: 2 3 4 * + = 14"""
        env, _ = rpn_env_and_output
        result = eval_source("(rpn \"2 3 4 * +\")", env)
        assert result == 14

    def test_rpn_operand_order_for_subtraction(self, rpn_env_and_output):
        """Test operand order: 10 2 3 - * = -10"""
        env, _ = rpn_env_and_output
        result = eval_source("(rpn \"10 2 3 - *\")", env)
        assert result == -10

    def test_rpn_single_number(self, rpn_env_and_output):
        """Test single number: 5 = 5"""
        env, _ = rpn_env_and_output
        result = eval_source("(rpn \"5\")", env)
        assert result == 5

    def test_rpn_multiple_additions(self, rpn_env_and_output):
        """Test multiple additions: 1 2 3 + + = 6"""
        env, _ = rpn_env_and_output
        result = eval_source("(rpn \"1 2 3 + +\")", env)
        assert result == 6

    def test_rpn_extra_whitespace(self, rpn_env_and_output):
        """Test extra whitespace tolerance: "  3   4  +  " = 7"""
        env, _ = rpn_env_and_output
        result = eval_source("(rpn \"  3   4  +  \")", env)
        assert result == 7

    def test_rpn_error_not_enough_operands(self, rpn_env_and_output):
        """Test error: 3 + should raise an error (not enough operands)"""
        env, _ = rpn_env_and_output
        with pytest.raises(Exception) as exc_info:
            eval_source("(rpn \"3 +\")", env)
        assert "not enough operands" in str(exc_info.value)

    def test_rpn_error_leftover_operands(self, rpn_env_and_output):
        """Test error: 3 4 should raise an error (leftover operands)"""
        env, _ = rpn_env_and_output
        with pytest.raises(Exception) as exc_info:
            eval_source("(rpn \"3 4\")", env)
        assert "leftover operands" in str(exc_info.value)

    def test_rpn_error_unknown_token(self, rpn_env_and_output):
        """Test error: 3 4 & should raise an error (unknown token)"""
        env, _ = rpn_env_and_output
        with pytest.raises(Exception) as exc_info:
            eval_source("(rpn \"3 4 &\")", env)
        assert "unknown token" in str(exc_info.value)

    def test_rpn_error_empty_input(self, rpn_env_and_output):
        """Test error: empty input should raise an error"""
        env, _ = rpn_env_and_output
        with pytest.raises(Exception) as exc_info:
            eval_source("(rpn \"\")", env)
        assert "empty stack" in str(exc_info.value)
