"""Tests for the Brainfuck interpreter example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


def _load_brainfuck_example():
    """Helper function to load brainfuck.pebble and capture its output."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "brainfuck.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def brainfuck_env_and_output():
    """Load brainfuck.pebble once and capture its output."""
    return _load_brainfuck_example()


class TestBrainfuckInterpreter:
    """Test cases for the Brainfuck interpreter."""

    def test_brainfuck_demo_output(self, brainfuck_env_and_output):
        """Test that running the brainfuck.pebble file produces 'HI'."""
        env, demo_output = brainfuck_env_and_output
        assert demo_output.strip() == "HI"

    def test_brainfuck_empty_program(self, brainfuck_env_and_output):
        """Test empty program returns empty output."""
        env, _ = brainfuck_env_and_output
        result = eval_source('(brainfuck "")', env)
        assert result == ""

    def test_brainfuck_no_output_command(self, brainfuck_env_and_output):
        """Test program with no output command."""
        env, _ = brainfuck_env_and_output
        result = eval_source('(brainfuck "+++")', env)
        assert result == ""

    def test_brainfuck_single_increment_output(self, brainfuck_env_and_output):
        """Test simple program: increment cell and output."""
        env, _ = brainfuck_env_and_output
        # cell0 = 1 (ASCII 1, not the character '1')
        result = eval_source('(brainfuck "+.")', env)
        assert result == chr(1)

    def test_brainfuck_char_65_A(self, brainfuck_env_and_output):
        """Test: cell0=8; loop adds 8 to cell1 eight times -> 64; then move right, +1 -> 65; output -> 'A'."""
        env, _ = brainfuck_env_and_output
        # ++++++++[>++++++++<-]>+.
        # cell0 = 8
        # [>++++++++<-] : move right, add 8, move left, decrement cell0, loop
        #   Each iteration: cell1 += 8, cell0 -= 1
        #   After 8 iterations: cell1 = 64, cell0 = 0
        # >+. : move right to cell1, increment to 65, output (char 65 is 'A')
        result = eval_source('(brainfuck "++++++++[>++++++++<-]>+.")', env)
        assert result == "A"

    def test_brainfuck_char_65_66_AB(self, brainfuck_env_and_output):
        """Test: after 'A', increment to 66 and output -> 'AB'."""
        env, _ = brainfuck_env_and_output
        # ++++++++[>++++++++<-]>+.+.
        # Same as above until output: cell1 = 65 (A)
        # . : output 'A'
        # + : increment to 66
        # . : output 'B'
        result = eval_source('(brainfuck "++++++++[>++++++++<-]>+.+.")', env)
        assert result == "AB"

    def test_brainfuck_72_73_HI(self, brainfuck_env_and_output):
        """Test: cell0=9; loop adds 8 nine times -> 72; output 'H'; +1 -> 73; output 'I'."""
        env, _ = brainfuck_env_and_output
        # +++++++++[>++++++++<-]>.+.
        # cell0 = 9
        # [>++++++++<-] : move right, add 8, move left, decrement
        #   Each iteration: cell1 += 8, cell0 -= 1
        #   After 9 iterations: cell1 = 72, cell0 = 0
        # >. : move right, output (char 72 is 'H')
        # +. : increment to 73, output (char 73 is 'I')
        result = eval_source('(brainfuck "+++++++++[>++++++++<-]>.+.")', env)
        assert result == "HI"

    def test_brainfuck_70_72_H(self, brainfuck_env_and_output):
        """Test: cell0=10; loop adds 7 ten times -> 70; +2 -> 72; output 'H'."""
        env, _ = brainfuck_env_and_output
        # ++++++++++[>+++++++<-]>++.
        # cell0 = 10
        # [>+++++++<-] : move right, add 7, move left, decrement
        #   Each iteration: cell1 += 7, cell0 -= 1
        #   After 10 iterations: cell1 = 70, cell0 = 0
        # >++. : move right, add 2 (to 72), output (char 72 is 'H')
        result = eval_source('(brainfuck "++++++++++[>+++++++<-]>++.")', env)
        assert result == "H"

    def test_brainfuck_cell_wrapping(self, brainfuck_env_and_output):
        """Test cell wrapping: 0 - 1 = 255."""
        env, _ = brainfuck_env_and_output
        # -. : decrement cell0 from 0 to 255 (wrap), output
        result = eval_source('(brainfuck "-.")', env)
        assert result == chr(255)

    def test_brainfuck_increment_wrapping(self, brainfuck_env_and_output):
        """Test cell wrapping: 255 + 1 = 0."""
        env, _ = brainfuck_env_and_output
        # We increment 255 times to get 255, then output.
        inc_program = "+" * 255 + "."
        result = eval_source(f'(brainfuck "{inc_program}")', env)
        assert ord(result) == 255

    def test_brainfuck_decrement_wrapping(self, brainfuck_env_and_output):
        """Test cell wrapping: 0 - 1 = 255."""
        env, _ = brainfuck_env_and_output
        # -. : decrement from 0 to 255 (wrap), output
        result = eval_source('(brainfuck "-.")', env)
        assert ord(result) == 255
