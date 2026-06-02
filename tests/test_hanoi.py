"""Tests for the Towers of Hanoi solver."""
import pytest
from io import StringIO
import sys
from pebble.evaluator import make_global_env, eval_source, seval
from pebble.types import Symbol, PebbleList


class TestHanoi:
    """Test the Towers of Hanoi solver."""

    @pytest.fixture
    def env_with_hanoi(self):
        """Create a global environment and load the hanoi.pebble file."""
        env = make_global_env()
        # Load the hanoi.pebble file
        with open('examples/hanoi.pebble', 'r') as f:
            source = f.read()
        # We need to suppress the print output from the demo
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            eval_source(source, env)
        finally:
            sys.stdout = old_stdout
        return env

    def test_hanoi_n0(self, env_with_hanoi):
        """Test hanoi-moves with n=0 returns nil (empty list)."""
        code = "(hanoi-moves 0 (quote a) (quote c) (quote b))"
        result = eval_source(code, env_with_hanoi)
        # Empty list should have length 0
        assert len(result) == 0

    def test_hanoi_n1(self, env_with_hanoi):
        """Test hanoi-moves with n=1 returns ((a c))."""
        code = "(hanoi-moves 1 (quote a) (quote c) (quote b))"
        result = eval_source(code, env_with_hanoi)
        # Result should be a list with one element
        assert len(result) == 1
        move = result[0]
        assert len(move) == 2
        assert move[0] == Symbol('a')
        assert move[1] == Symbol('c')

    def test_hanoi_n2(self, env_with_hanoi):
        """Test hanoi-moves with n=2 returns ((a b) (a c) (b c))."""
        code = "(hanoi-moves 2 (quote a) (quote c) (quote b))"
        result = eval_source(code, env_with_hanoi)
        # Result should have 3 moves: 2^2 - 1 = 3
        assert len(result) == 3

        # Verify each move
        expected = [
            (Symbol('a'), Symbol('b')),
            (Symbol('a'), Symbol('c')),
            (Symbol('b'), Symbol('c')),
        ]
        for i, (src, dst) in enumerate(expected):
            assert result[i][0] == src, f"Move {i}: src should be {src}, got {result[i][0]}"
            assert result[i][1] == dst, f"Move {i}: dst should be {dst}, got {result[i][1]}"

    def test_hanoi_n3(self, env_with_hanoi):
        """Test hanoi-moves with n=3 returns 7 moves in the correct order."""
        code = "(hanoi-moves 3 (quote a) (quote c) (quote b))"
        result = eval_source(code, env_with_hanoi)
        # Result should have 7 moves: 2^3 - 1 = 7
        assert len(result) == 7

        # Verify the sequence
        expected = [
            (Symbol('a'), Symbol('c')),
            (Symbol('a'), Symbol('b')),
            (Symbol('c'), Symbol('b')),
            (Symbol('a'), Symbol('c')),
            (Symbol('b'), Symbol('a')),
            (Symbol('b'), Symbol('c')),
            (Symbol('a'), Symbol('c')),
        ]
        for i, (src, dst) in enumerate(expected):
            assert result[i][0] == src, f"Move {i}: src should be {src}, got {result[i][0]}"
            assert result[i][1] == dst, f"Move {i}: dst should be {dst}, got {result[i][1]}"

    def test_hanoi_n4_length(self, env_with_hanoi):
        """Test hanoi-moves with n=4 returns 15 moves (2^4 - 1)."""
        code = "(length (hanoi-moves 4 (quote a) (quote c) (quote b)))"
        result = eval_source(code, env_with_hanoi)
        assert result == 15

    def test_hanoi_n6_length(self, env_with_hanoi):
        """Test hanoi-moves with n=6 returns 63 moves (2^6 - 1)."""
        code = "(length (hanoi-moves 6 (quote a) (quote c) (quote b)))"
        result = eval_source(code, env_with_hanoi)
        assert result == 63

    def test_hanoi_demo_output(self, capsys):
        """Test that the hanoi.pebble file prints the correct demo output."""
        env = make_global_env()
        with open('examples/hanoi.pebble', 'r') as f:
            source = f.read()
        eval_source(source, env)

        captured = capsys.readouterr()
        expected_lines = [
            "a -> c",
            "a -> b",
            "c -> b",
            "a -> c",
            "b -> a",
            "b -> c",
            "a -> c",
        ]
        expected_output = "\n".join(expected_lines) + "\n"
        assert captured.out == expected_output
