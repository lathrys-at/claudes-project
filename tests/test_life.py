"""Tests for the Conway's Game of Life example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


def _load_life_example():
    """Helper function to load life.pebble and capture its output."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "life.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def life_env_and_output():
    """Load life.pebble once and capture its output."""
    return _load_life_example()


class TestLife:
    """Tests for the Conway's Game of Life example."""

    def test_life_output(self, life_env_and_output):
        """Test that the Game of Life produces the correct blinker pattern."""
        env, demo_output = life_env_and_output

        # Expected output: generation 0 (horizontal blinker), blank line,
        # generation 1 (vertical blinker), blank line, generation 2 (back to horizontal)
        expected_output = (
            ".....\n"
            ".....\n"
            ".###.\n"
            ".....\n"
            ".....\n"
            "\n"
            ".....\n"
            "..#..\n"
            "..#..\n"
            "..#..\n"
            ".....\n"
            "\n"
            ".....\n"
            ".....\n"
            ".###.\n"
            ".....\n"
            "....."
        )

        # Strip trailing whitespace from the actual output for comparison
        actual_output = demo_output.rstrip()
        expected_output = expected_output.rstrip()

        assert actual_output == expected_output

    def test_life_grid_construction(self, life_env_and_output):
        """Test that the grid is constructed using mutable vectors."""
        env, _ = life_env_and_output

        # Verify that make-grid, grid-get, and grid-set! functions exist
        assert env.lookup("make-grid") is not None
        assert env.lookup("grid-get") is not None
        assert env.lookup("grid-set!") is not None
        assert env.lookup("next-generation") is not None

    def test_life_period_2_oscillator(self, life_env_and_output):
        """Test that the blinker oscillates with period 2 by checking the output."""
        env, output = life_env_and_output

        # The output should contain three generations separated by blank lines
        lines = output.split('\n')

        # Extract the three generations (each 5 lines)
        gen0_lines = lines[0:5]
        gen1_lines = lines[6:11]  # Skip blank line at index 5
        gen2_lines = lines[12:17]  # Skip blank line at index 11

        # Generation 0: horizontal blinker
        assert gen0_lines[2] == ".###."

        # Generation 1: vertical blinker (should have # in middle column)
        assert gen1_lines[1] == "..#.."
        assert gen1_lines[2] == "..#.."
        assert gen1_lines[3] == "..#.."

        # Generation 2: back to horizontal blinker
        assert gen2_lines[2] == ".###."
