"""Tests for lazy streams example built on delay/force."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


def _load_streams_example():
    """Helper function to load streams.pebble and capture its output."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "streams.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def streams_env_and_output():
    """Load streams.pebble once and capture its output."""
    return _load_streams_example()


class TestLazyStreams:
    """Tests for the lazy streams example program."""

    def test_demo_output(self, streams_env_and_output):
        """Test that the streams example produces the correct demo output."""
        env, demo_output = streams_env_and_output

        expected_lines = [
            "(1 2 3 4 5 6 7 8 9 10)",
            "(1 4 9 16 25)"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_stream_take_5_from_1(self, streams_env_and_output):
        """Test that (stream-take (integers-from 1) 5) returns (1 2 3 4 5)."""
        env, _ = streams_env_and_output

        code = "(stream-take (integers-from 1) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((1, 2, 3, 4, 5))

    def test_stream_take_3_from_10(self, streams_env_and_output):
        """Test that (stream-take (integers-from 10) 3) returns (10 11 12)."""
        env, _ = streams_env_and_output

        code = "(stream-take (integers-from 10) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((10, 11, 12))

    def test_stream_car_from_7(self, streams_env_and_output):
        """Test that (stream-car (integers-from 7)) returns 7."""
        env, _ = streams_env_and_output

        code = "(stream-car (integers-from 7))"
        result = eval_source(code, env)
        assert result == 7

    def test_stream_car_of_cdr_from_7(self, streams_env_and_output):
        """Test that (stream-car (stream-cdr (integers-from 7))) returns 8."""
        env, _ = streams_env_and_output

        code = "(stream-car (stream-cdr (integers-from 7)))"
        result = eval_source(code, env)
        assert result == 8

    def test_stream_map_squares(self, streams_env_and_output):
        """Test that stream-map applies a function lazily.

        (stream-take (stream-map (lambda (x) (* x x)) (integers-from 1)) 5)
        should return (1 4 9 16 25).
        """
        env, _ = streams_env_and_output

        code = "(stream-take (stream-map (lambda (x) (* x x)) (integers-from 1)) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((1, 4, 9, 16, 25))

    def test_stream_take_0(self, streams_env_and_output):
        """Test that (stream-take (integers-from 1) 0) returns nil (empty list)."""
        env, _ = streams_env_and_output

        code = "(stream-take (integers-from 1) 0)"
        result = eval_source(code, env)
        assert result == PebbleList(())  # empty list

    def test_infinite_stream_terminates(self, streams_env_and_output):
        """Test that integers-from creates an infinite but lazy stream.

        This test demonstrates laziness: integers-from would loop forever if not lazy,
        but stream-take terminates because the tail is delayed (not forced until needed).
        """
        env, _ = streams_env_and_output

        # This would hang forever if integers-from eagerly evaluated its tail
        code = "(stream-take (integers-from 1) 100)"
        result = eval_source(code, env)

        # Verify it actually produced 100 elements
        assert len(result) == 100
        assert result[0] == 1
        assert result[99] == 100

    def test_stream_cons_is_macro(self, streams_env_and_output):
        """Test that stream-cons is a macro that delays its tail.

        If stream-cons were a regular function, (stream-cons 1 (integers-from 2))
        would hang because integers-from 2 would be eagerly evaluated.
        Since stream-cons is a macro, it delays (integers-from 2), so it works.
        """
        env, _ = streams_env_and_output

        # This would hang if stream-cons weren't a macro
        code = "(stream-take (stream-cons 1 (integers-from 2)) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((1, 2, 3))
