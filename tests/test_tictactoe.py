"""Tests for the tic-tac-toe win detection example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


@pytest.fixture(scope="module")
def tictactoe_env_and_output():
    """Load the tictactoe.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "tictactoe.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestTictactoe:
    """Tests for tic-tac-toe win detection."""

    def test_example_output(self, tictactoe_env_and_output):
        """Test that the example file produces the correct demo output."""
        env, demo_output = tictactoe_env_and_output

        expected_lines = [
            "x",
            "nil"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_winner_top_row(self, tictactoe_env_and_output):
        """Test X wins with top row."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list 'x 'x 'x '- '- '- '- '- '-))", env)
        assert result == eval_source("'x", env)

    def test_winner_bottom_row(self, tictactoe_env_and_output):
        """Test O wins with bottom row."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list '- '- '- '- '- '- 'o 'o 'o))", env)
        assert result == eval_source("'o", env)

    def test_winner_left_column(self, tictactoe_env_and_output):
        """Test X wins with left column."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list 'x '- '- 'x '- '- 'x '- '-))", env)
        assert result == eval_source("'x", env)

    def test_winner_main_diagonal(self, tictactoe_env_and_output):
        """Test X wins with main diagonal (0 4 8)."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list 'x '- '- '- 'x '- '- '- 'x))", env)
        assert result == eval_source("'x", env)

    def test_winner_anti_diagonal(self, tictactoe_env_and_output):
        """Test O wins with anti-diagonal (2 4 6)."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list '- '- 'o '- 'o '- 'o '- '-))", env)
        assert result == eval_source("'o", env)

    def test_winner_full_board_no_line(self, tictactoe_env_and_output):
        """Test that a full board with no three in a row returns nil."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list 'x 'o 'x 'o 'x 'o 'o 'x 'o))", env)
        # nil in Pebble is represented as an empty PebbleList
        assert isinstance(result, PebbleList) and len(result) == 0

    def test_winner_empty_board(self, tictactoe_env_and_output):
        """Test that an empty board returns nil."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list '- '- '- '- '- '- '- '- '-))", env)
        # nil in Pebble is represented as an empty PebbleList
        assert isinstance(result, PebbleList) and len(result) == 0

    def test_winner_no_three_in_row(self, tictactoe_env_and_output):
        """Test that a partial board with no three in a row returns nil."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list 'x 'o 'x 'x 'o 'o 'o 'x 'x))", env)
        # nil in Pebble is represented as an empty PebbleList
        assert isinstance(result, PebbleList) and len(result) == 0

    def test_winner_middle_row(self, tictactoe_env_and_output):
        """Test X wins with middle row."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list '- '- '- 'x 'x 'x '- '- '-))", env)
        assert result == eval_source("'x", env)

    def test_winner_middle_column(self, tictactoe_env_and_output):
        """Test O wins with middle column."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list '- 'o '- '- 'o '- '- 'o '-))", env)
        assert result == eval_source("'o", env)

    def test_winner_right_column(self, tictactoe_env_and_output):
        """Test X wins with right column."""
        env, _ = tictactoe_env_and_output

        result = eval_source("(winner (list '- '- 'x '- '- 'x '- '- 'x))", env)
        assert result == eval_source("'x", env)
