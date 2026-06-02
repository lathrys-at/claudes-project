"""Tests for the edit distance example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


@pytest.fixture(scope="module")
def edit_distance_env_and_output():
    """Load the edit_distance.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "edit_distance.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestEditDistance:
    """Tests for the Levenshtein edit distance example."""

    def test_example_output(self, edit_distance_env_and_output):
        """Test that the example file produces the correct output."""
        env, demo_output = edit_distance_env_and_output

        # The demo line should be "3" (edit-distance "kitten" "sitting")
        output_line = demo_output.strip()
        assert output_line == "3", f"Expected demo output '3', got '{output_line}'"

    def test_kitten_sitting(self, edit_distance_env_and_output):
        """Test the classic kitten/sitting case: should be 3."""
        env, _ = edit_distance_env_and_output
        result = eval_source('(edit-distance "kitten" "sitting")', env)
        assert result == 3

    def test_empty_strings(self, edit_distance_env_and_output):
        """Test edit distance between two empty strings."""
        env, _ = edit_distance_env_and_output
        result = eval_source('(edit-distance "" "")', env)
        assert result == 0

    def test_identical_strings(self, edit_distance_env_and_output):
        """Test edit distance between identical strings."""
        env, _ = edit_distance_env_and_output
        result = eval_source('(edit-distance "abc" "abc")', env)
        assert result == 0

    def test_empty_to_nonempty(self, edit_distance_env_and_output):
        """Test edit distance from empty string to non-empty string."""
        env, _ = edit_distance_env_and_output
        result = eval_source('(edit-distance "" "abc")', env)
        assert result == 3

    def test_nonempty_to_empty(self, edit_distance_env_and_output):
        """Test edit distance from non-empty string to empty string."""
        env, _ = edit_distance_env_and_output
        result = eval_source('(edit-distance "abc" "")', env)
        assert result == 3

    def test_single_char_different(self, edit_distance_env_and_output):
        """Test edit distance between two different single characters."""
        env, _ = edit_distance_env_and_output
        result = eval_source('(edit-distance "a" "b")', env)
        assert result == 1

    def test_flaw_lawn(self, edit_distance_env_and_output):
        """Test flaw -> lawn: should be 2."""
        env, _ = edit_distance_env_and_output
        result = eval_source('(edit-distance "flaw" "lawn")', env)
        assert result == 2

    def test_sunday_saturday(self, edit_distance_env_and_output):
        """Test sunday -> saturday: should be 3."""
        env, _ = edit_distance_env_and_output
        result = eval_source('(edit-distance "sunday" "saturday")', env)
        assert result == 3

    def test_book_back(self, edit_distance_env_and_output):
        """Test book -> back: should be 2."""
        env, _ = edit_distance_env_and_output
        result = eval_source('(edit-distance "book" "back")', env)
        assert result == 2

    def test_symmetry(self, edit_distance_env_and_output):
        """Test that edit distance is symmetric."""
        env, _ = edit_distance_env_and_output
        result1 = eval_source('(edit-distance "kitten" "sitting")', env)
        result2 = eval_source('(edit-distance "sitting" "kitten")', env)
        assert result1 == result2
        assert result1 == 3
