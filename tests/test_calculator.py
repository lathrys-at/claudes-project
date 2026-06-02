"""Tests for the calculator example program."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source


class TestCalculator:
    """Tests for the calculator arithmetic expression evaluator."""

    @pytest.fixture
    def calc_env(self):
        """Load the calculator module and return the environment with calc defined."""
        calc_file = Path(__file__).parent.parent / "examples" / "calculator.pebble"
        with open(calc_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
        return env

    def test_calc_demo_output(self, calc_env, capsys):
        """Test that the calculator demo output is correct when loaded."""
        calc_file = Path(__file__).parent.parent / "examples" / "calculator.pebble"
        with open(calc_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        captured = capsys.readouterr()
        expected_lines = [
            "2 + 3 = 5",
            "2 + 3 * 4 = 14",
            "(2 + 3) * 4 = 20"
        ]
        output_lines = captured.out.strip().split('\n')
        assert output_lines == expected_lines

    def test_calc_simple_addition(self, calc_env):
        """Test simple addition: 2 + 3 = 5"""
        result = eval_source('(calc "2 + 3")', calc_env)
        assert result == 5

    def test_calc_addition_no_spaces(self, calc_env):
        """Test addition without spaces: 2+3 = 5"""
        result = eval_source('(calc "2+3")', calc_env)
        assert result == 5

    def test_calc_with_precedence(self, calc_env):
        """Test operator precedence: 2 + 3 * 4 = 14"""
        result = eval_source('(calc "2 + 3 * 4")', calc_env)
        assert result == 14

    def test_calc_with_parentheses(self, calc_env):
        """Test parentheses override precedence: (2 + 3) * 4 = 20"""
        result = eval_source('(calc "(2 + 3) * 4")', calc_env)
        assert result == 20

    def test_calc_left_associative_subtraction(self, calc_env):
        """Test left-associativity of subtraction: 10 - 4 - 3 = 3"""
        result = eval_source('(calc "10 - 4 - 3")', calc_env)
        assert result == 3

    def test_calc_mixed_operators(self, calc_env):
        """Test mixed operators with precedence: 2 * 3 + 4 * 5 = 26"""
        result = eval_source('(calc "2 * 3 + 4 * 5")', calc_env)
        assert result == 26

    def test_calc_nested_parentheses(self, calc_env):
        """Test nested parentheses: ((1 + 2) * (3 + 4)) = 21"""
        result = eval_source('(calc "((1 + 2) * (3 + 4))")', calc_env)
        assert result == 21

    def test_calc_single_number(self, calc_env):
        """Test single number: 7 = 7"""
        result = eval_source('(calc "7")', calc_env)
        assert result == 7

    def test_calc_multiplication_by_zero(self, calc_env):
        """Test multiplication by zero: 100 * 0 + 42 = 42"""
        result = eval_source('(calc "100 * 0 + 42")', calc_env)
        assert result == 42

    def test_calc_left_associative_addition(self, calc_env):
        """Test left-associativity with addition: 1 + 2 + 3 + 4 + 5 = 15"""
        result = eval_source('(calc "1 + 2 + 3 + 4 + 5")', calc_env)
        assert result == 15

    def test_calc_complex_nested(self, calc_env):
        """Test complex nested expression: 2 * (3 + (4 * 5)) = 46"""
        result = eval_source('(calc "2 * (3 + (4 * 5))")', calc_env)
        assert result == 46
