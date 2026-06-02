"""Tests for lazy Sieve of Eratosthenes prime-stream example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


def _load_primes_example():
    """Helper function to load primes.pebble and capture its output."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "primes.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def primes_env_and_output():
    """Load primes.pebble once and capture its output."""
    return _load_primes_example()


class TestLazySieveOfEratosthenes:
    """Tests for the lazy Sieve of Eratosthenes prime-stream example."""

    def test_demo_output(self, primes_env_and_output):
        """Test that the primes example produces the correct demo output."""
        env, demo_output = primes_env_and_output

        expected_lines = [
            "(2 3 5 7 11 13 17 19 23 29)",
            "(2 4 6 8 10)"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_stream_take_10_primes(self, primes_env_and_output):
        """Test that (stream-take primes 10) returns the first 10 primes."""
        env, _ = primes_env_and_output

        code = "(stream-take primes 10)"
        result = eval_source(code, env)
        assert result == PebbleList((2, 3, 5, 7, 11, 13, 17, 19, 23, 29))

    def test_stream_take_5_primes(self, primes_env_and_output):
        """Test that (stream-take primes 5) returns the first 5 primes."""
        env, _ = primes_env_and_output

        code = "(stream-take primes 5)"
        result = eval_source(code, env)
        assert result == PebbleList((2, 3, 5, 7, 11))

    def test_stream_car_primes(self, primes_env_and_output):
        """Test that (stream-car primes) returns 2 (the first prime)."""
        env, _ = primes_env_and_output

        code = "(stream-car primes)"
        result = eval_source(code, env)
        assert result == 2

    def test_stream_car_cdr_primes(self, primes_env_and_output):
        """Test that (stream-car (stream-cdr primes)) returns 3 (the second prime)."""
        env, _ = primes_env_and_output

        code = "(stream-car (stream-cdr primes))"
        result = eval_source(code, env)
        assert result == 3

    def test_stream_filter_even_numbers(self, primes_env_and_output):
        """Test that stream-filter works correctly on an infinite stream.

        (stream-take (stream-filter even? (integers-from 1)) 5)
        should return (2 4 6 8 10).
        """
        env, _ = primes_env_and_output

        code = "(stream-take (stream-filter even? (integers-from 1)) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((2, 4, 6, 8, 10))

    def test_infinite_prime_stream_terminates(self, primes_env_and_output):
        """Test that the prime sieve creates an infinite but lazy stream.

        This test demonstrates laziness: the sieve would loop forever if not lazy,
        but stream-take terminates because the tail is delayed (not forced until needed).
        The fact that this test completes proves that stream-cons is a macro that
        properly delays its tail.
        """
        env, _ = primes_env_and_output

        # This would hang forever if the sieve eagerly evaluated its tail
        code = "(stream-take primes 50)"
        result = eval_source(code, env)

        # Verify it actually produced 50 primes
        assert len(result) == 50
        assert result[0] == 2
        # The 50th prime is 229
        assert result[49] == 229

    def test_stream_cons_is_macro(self, primes_env_and_output):
        """Test that stream-cons is a macro that delays its tail.

        If stream-cons were a regular function, the primes definition itself
        would hang because the sieve would be eagerly evaluated.
        Since stream-cons is a macro, it delays the sieve, so it works.
        The fact that primes is defined and usable proves this.
        """
        env, _ = primes_env_and_output

        # If stream-cons weren't a macro, primes would never be defined
        # because sieve would infinitely loop. This test confirms that
        # stream-cons properly delays its tail.
        code = "(stream-take (stream-cons 2 (stream-cons 3 (stream-cons 5 nil))) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((2, 3, 5))
