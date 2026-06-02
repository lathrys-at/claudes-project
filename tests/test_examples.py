"""Tests for example Pebble programs."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source


class TestExamples:
    """Tests for the example programs in examples/ directory."""

    def test_fizzbuzz(self, capsys):
        """Test FizzBuzz example."""
        example_file = Path(__file__).parent.parent / "examples" / "fizzbuzz.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        captured = capsys.readouterr()
        expected_lines = [
            "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz",
            "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"
        ]
        output_lines = captured.out.strip().split('\n')
        assert output_lines == expected_lines

    def test_fibonacci(self, capsys):
        """Test Fibonacci example."""
        example_file = Path(__file__).parent.parent / "examples" / "fibonacci.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        captured = capsys.readouterr()
        expected = "0 1 1 2 3 5 8 13 21 34"
        assert captured.out.strip() == expected

    def test_quicksort(self, capsys):
        """Test Quicksort example."""
        example_file = Path(__file__).parent.parent / "examples" / "quicksort.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        captured = capsys.readouterr()
        expected = "(1 2 3 4 6 8 9)"
        assert captured.out.strip() == expected

    def test_wordcount(self, capsys):
        """Test Word count example."""
        example_file = Path(__file__).parent.parent / "examples" / "wordcount.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        captured = capsys.readouterr()
        expected_lines = [
            "apple: 3",
            "banana: 2",
            "cherry: 1"
        ]
        output_lines = captured.out.strip().split('\n')
        assert output_lines == expected_lines

    def test_error_handling(self, capsys):
        """Test Error handling example."""
        example_file = Path(__file__).parent.parent / "examples" / "error_handling.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)

        captured = capsys.readouterr()
        expected_lines = [
            "caught: something went wrong",
            "result: 30"
        ]
        output_lines = captured.out.strip().split('\n')
        assert output_lines == expected_lines
