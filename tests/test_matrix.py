"""Tests for the matrix library example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


def _load_matrix_example():
    """Helper function to load matrix.pebble and capture its output."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "matrix.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def matrix_env_and_output():
    """Load matrix.pebble once and capture its output."""
    return _load_matrix_example()


class TestMatrixLibrary:
    """Tests for the matrix library example program."""

    def test_demo_output(self, matrix_env_and_output):
        """Test that the matrix example produces the correct demo output."""
        env, demo_output = matrix_env_and_output

        expected_lines = [
            "((1 4) (2 5) (3 6))",
            "((19 22) (43 50))"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_mat_transpose_2x3(self, matrix_env_and_output):
        """Test transpose of a 2x3 matrix."""
        env, demo_output = matrix_env_and_output

        code = "(mat-transpose (list (list 1 2 3) (list 4 5 6)))"
        result = eval_source(code, env)
        expected = PebbleList((
            PebbleList((1, 4)),
            PebbleList((2, 5)),
            PebbleList((3, 6))
        ))
        assert result == expected

    def test_mat_transpose_2x2(self, matrix_env_and_output):
        """Test transpose of a 2x2 matrix."""
        env, demo_output = matrix_env_and_output

        code = "(mat-transpose (list (list 1 2) (list 3 4)))"
        result = eval_source(code, env)
        expected = PebbleList((
            PebbleList((1, 3)),
            PebbleList((2, 4))
        ))
        assert result == expected

    def test_mat_mul_2x2(self, matrix_env_and_output):
        """Test matrix multiplication of two 2x2 matrices."""
        env, demo_output = matrix_env_and_output

        code = "(mat-mul (list (list 1 2) (list 3 4)) (list (list 5 6) (list 7 8)))"
        result = eval_source(code, env)
        expected = PebbleList((
            PebbleList((19, 22)),
            PebbleList((43, 50))
        ))
        assert result == expected

    def test_mat_mul_2x3_times_3x2(self, matrix_env_and_output):
        """Test matrix multiplication of 2x3 times 3x2 matrices."""
        env, demo_output = matrix_env_and_output

        code = "(mat-mul (list (list 1 2 3) (list 4 5 6)) (list (list 7 8) (list 9 10) (list 11 12)))"
        result = eval_source(code, env)
        expected = PebbleList((
            PebbleList((58, 64)),
            PebbleList((139, 154))
        ))
        assert result == expected

    def test_mat_add_2x2(self, matrix_env_and_output):
        """Test element-wise addition of two 2x2 matrices."""
        env, demo_output = matrix_env_and_output

        code = "(mat-add (list (list 1 2) (list 3 4)) (list (list 10 20) (list 30 40)))"
        result = eval_source(code, env)
        expected = PebbleList((
            PebbleList((11, 22)),
            PebbleList((33, 44))
        ))
        assert result == expected

    def test_identity_matrix_3x3(self, matrix_env_and_output):
        """Test identity matrix of size 3x3."""
        env, demo_output = matrix_env_and_output

        code = "(identity-matrix 3)"
        result = eval_source(code, env)
        expected = PebbleList((
            PebbleList((1, 0, 0)),
            PebbleList((0, 1, 0)),
            PebbleList((0, 0, 1))
        ))
        assert result == expected

    def test_identity_matrix_1x1(self, matrix_env_and_output):
        """Test identity matrix of size 1x1."""
        env, demo_output = matrix_env_and_output

        code = "(identity-matrix 1)"
        result = eval_source(code, env)
        expected = PebbleList((
            PebbleList((1,)),
        ))
        assert result == expected

    def test_transpose_twice_returns_original(self, matrix_env_and_output):
        """Test that transposing twice returns the original matrix."""
        env, demo_output = matrix_env_and_output

        code = "(mat-transpose (mat-transpose (list (list 1 2 3) (list 4 5 6))))"
        result = eval_source(code, env)
        expected = PebbleList((
            PebbleList((1, 2, 3)),
            PebbleList((4, 5, 6))
        ))
        assert result == expected
