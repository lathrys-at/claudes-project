"""Tests for the Towers of Hanoi solver."""
import pytest
from io import StringIO
import sys
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source, seval
from pebble.types import Symbol, PebbleList


def _load_hanoi_example():
    """Helper function to load hanoi.pebble and capture its output."""
    env = make_global_env()
    # Load the hanoi.pebble file
    hanoi_file = Path(__file__).parent.parent / "examples" / "hanoi.pebble"
    with open(hanoi_file, 'r') as f:
        source = f.read()
    # We need to suppress the print output from the demo
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    try:
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout
    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def hanoi_env_and_output():
    """Load hanoi.pebble once and capture its output."""
    return _load_hanoi_example()


class TestHanoi:
    """Test the Towers of Hanoi solver."""

    def test_hanoi_n0(self, hanoi_env_and_output):
        """Test hanoi-moves with n=0 returns nil (empty list)."""
        env, _ = hanoi_env_and_output
        code = "(hanoi-moves 0 (quote a) (quote c) (quote b))"
        result = eval_source(code, env)
        # Empty list should have length 0
        assert len(result) == 0

    def test_hanoi_n1(self, hanoi_env_and_output):
        """Test hanoi-moves with n=1 returns ((a c))."""
        env, _ = hanoi_env_and_output
        code = "(hanoi-moves 1 (quote a) (quote c) (quote b))"
        result = eval_source(code, env)
        # Result should be a list with one element
        assert len(result) == 1
        move = result[0]
        assert len(move) == 2
        assert move[0] == Symbol('a')
        assert move[1] == Symbol('c')

    def test_hanoi_n2(self, hanoi_env_and_output):
        """Test hanoi-moves with n=2 returns ((a b) (a c) (b c))."""
        env, _ = hanoi_env_and_output
        code = "(hanoi-moves 2 (quote a) (quote c) (quote b))"
        result = eval_source(code, env)
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

    def test_hanoi_n3(self, hanoi_env_and_output):
        """Test hanoi-moves with n=3 returns 7 moves in the correct order."""
        env, _ = hanoi_env_and_output
        code = "(hanoi-moves 3 (quote a) (quote c) (quote b))"
        result = eval_source(code, env)
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

    def test_hanoi_n4_length(self, hanoi_env_and_output):
        """Test hanoi-moves with n=4 returns 15 moves (2^4 - 1)."""
        env, _ = hanoi_env_and_output
        code = "(length (hanoi-moves 4 (quote a) (quote c) (quote b)))"
        result = eval_source(code, env)
        assert result == 15

    def test_hanoi_n6_length(self, hanoi_env_and_output):
        """Test hanoi-moves with n=6 returns 63 moves (2^6 - 1)."""
        env, _ = hanoi_env_and_output
        code = "(length (hanoi-moves 6 (quote a) (quote c) (quote b)))"
        result = eval_source(code, env)
        assert result == 63

    def test_hanoi_demo_output(self, hanoi_env_and_output):
        """Test that the hanoi.pebble file prints the correct demo output."""
        env, demo_output = hanoi_env_and_output
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
        assert demo_output == expected_output
