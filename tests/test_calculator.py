"""Tests for the calculator example program."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


@pytest.fixture(scope="module")
def calc_env_and_output():
    """Load the calculator.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        calc_file = Path(__file__).parent.parent / "examples" / "calculator.pebble"
        with open(calc_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestCalculator:
    """Tests for the calculator arithmetic expression evaluator."""

    def test_calc_demo_output(self, calc_env_and_output):
        """Test that the calculator demo output is correct when loaded."""
        env, demo_output = calc_env_and_output

        expected_lines = [
            "2 + 3 = 5",
            "2 + 3 * 4 = 14",
            "(2 + 3) * 4 = 20"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_calc_simple_addition(self, calc_env_and_output):
        """Test simple addition: 2 + 3 = 5"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "2 + 3")', env)
        assert result == 5

    def test_calc_addition_no_spaces(self, calc_env_and_output):
        """Test addition without spaces: 2+3 = 5"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "2+3")', env)
        assert result == 5

    def test_calc_with_precedence(self, calc_env_and_output):
        """Test operator precedence: 2 + 3 * 4 = 14"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "2 + 3 * 4")', env)
        assert result == 14

    def test_calc_with_parentheses(self, calc_env_and_output):
        """Test parentheses override precedence: (2 + 3) * 4 = 20"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "(2 + 3) * 4")', env)
        assert result == 20

    def test_calc_left_associative_subtraction(self, calc_env_and_output):
        """Test left-associativity of subtraction: 10 - 4 - 3 = 3"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "10 - 4 - 3")', env)
        assert result == 3

    def test_calc_mixed_operators(self, calc_env_and_output):
        """Test mixed operators with precedence: 2 * 3 + 4 * 5 = 26"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "2 * 3 + 4 * 5")', env)
        assert result == 26

    def test_calc_nested_parentheses(self, calc_env_and_output):
        """Test nested parentheses: ((1 + 2) * (3 + 4)) = 21"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "((1 + 2) * (3 + 4))")', env)
        assert result == 21

    def test_calc_single_number(self, calc_env_and_output):
        """Test single number: 7 = 7"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "7")', env)
        assert result == 7

    def test_calc_multiplication_by_zero(self, calc_env_and_output):
        """Test multiplication by zero: 100 * 0 + 42 = 42"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "100 * 0 + 42")', env)
        assert result == 42

    def test_calc_left_associative_addition(self, calc_env_and_output):
        """Test left-associativity with addition: 1 + 2 + 3 + 4 + 5 = 15"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "1 + 2 + 3 + 4 + 5")', env)
        assert result == 15

    def test_calc_complex_nested(self, calc_env_and_output):
        """Test complex nested expression: 2 * (3 + (4 * 5)) = 46"""
        env, _ = calc_env_and_output
        result = eval_source('(calc "2 * (3 + (4 * 5))")', env)
        assert result == 46
