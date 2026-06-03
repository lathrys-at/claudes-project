"""Tests for the Pascal's triangle example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


@pytest.fixture(scope="module")
def pascal_env_and_output():
    """Load the pascal.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "pascal.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestPascal:
    """Tests for the Pascal's triangle generator."""

    def test_example_output(self, pascal_env_and_output):
        """Test that the example file produces the correct demo output."""
        env, demo_output = pascal_env_and_output

        expected = "((1) (1 1) (1 2 1) (1 3 3 1) (1 4 6 4 1))\n"
        assert demo_output == expected

    def test_pascal_0(self, pascal_env_and_output):
        """Test pascal(0) returns empty list."""
        env, _ = pascal_env_and_output

        result = eval_source("(pascal 0)", env)
        # nil is represented as an empty PebbleList
        assert isinstance(result, PebbleList)
        assert len(result) == 0

    def test_pascal_1(self, pascal_env_and_output):
        """Test pascal(1) returns ((1))."""
        env, _ = pascal_env_and_output

        result = eval_source("(pascal 1)", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 1
        row1 = result[0]
        assert isinstance(row1, PebbleList)
        assert len(row1) == 1
        assert row1[0] == 1

    def test_pascal_2(self, pascal_env_and_output):
        """Test pascal(2) returns ((1) (1 1))."""
        env, _ = pascal_env_and_output

        result = eval_source("(pascal 2)", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 2

        row1 = result[0]
        assert len(row1) == 1
        assert row1[0] == 1

        row2 = result[1]
        assert len(row2) == 2
        assert row2[0] == 1
        assert row2[1] == 1

    def test_pascal_3(self, pascal_env_and_output):
        """Test pascal(3) returns ((1) (1 1) (1 2 1))."""
        env, _ = pascal_env_and_output

        result = eval_source("(pascal 3)", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 3

        # Row 1: (1)
        row1 = result[0]
        assert list(row1) == [1]

        # Row 2: (1 1)
        row2 = result[1]
        assert list(row2) == [1, 1]

        # Row 3: (1 2 1)
        row3 = result[2]
        assert list(row3) == [1, 2, 1]

    def test_pascal_5(self, pascal_env_and_output):
        """Test pascal(5) returns ((1) (1 1) (1 2 1) (1 3 3 1) (1 4 6 4 1))."""
        env, _ = pascal_env_and_output

        result = eval_source("(pascal 5)", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 5

        expected_rows = [
            [1],
            [1, 1],
            [1, 2, 1],
            [1, 3, 3, 1],
            [1, 4, 6, 4, 1]
        ]
        for i, expected_row in enumerate(expected_rows):
            row = result[i]
            assert list(row) == expected_row

    def test_pascal_row_6_sum(self, pascal_env_and_output):
        """Test row-sum property: sum of row 6 (index 5) is 2^5 = 32."""
        env, _ = pascal_env_and_output

        result = eval_source("(sum (nth (pascal 6) 5))", env)
        assert result == 32

    def test_pascal_row_7_index_6(self, pascal_env_and_output):
        """Test specific row: (nth (pascal 7) 6) is (1 6 15 20 15 6 1)."""
        env, _ = pascal_env_and_output

        result = eval_source("(nth (pascal 7) 6)", env)
        assert isinstance(result, PebbleList)
        expected = [1, 6, 15, 20, 15, 6, 1]
        assert list(result) == expected
