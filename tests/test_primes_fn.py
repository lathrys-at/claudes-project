"""
Tests for number-theory functions: prime? and primes-up-to
"""
import pytest
from pebble.evaluator import make_global_env, eval_source


def evaluate_pebble(source: str):
    """Evaluate a Pebble source expression and return the result."""
    env = make_global_env()
    return eval_source(source, env)


class TestPrimeFunction:
    """Tests for the prime? function."""

    def test_prime_small_primes(self):
        """Test that small primes are correctly identified."""
        assert evaluate_pebble("(prime? 2)") is True
        assert evaluate_pebble("(prime? 3)") is True
        assert evaluate_pebble("(prime? 5)") is True
        assert evaluate_pebble("(prime? 7)") is True

    def test_prime_large_prime(self):
        """Test that 97 (a large prime) is correctly identified."""
        assert evaluate_pebble("(prime? 97)") is True

    def test_prime_small_composites(self):
        """Test that small composite numbers are correctly identified as not prime."""
        assert evaluate_pebble("(prime? 4)") is False
        assert evaluate_pebble("(prime? 9)") is False

    def test_prime_larger_composites(self):
        """Test that larger composite numbers are correctly identified as not prime."""
        assert evaluate_pebble("(prime? 100)") is False

    def test_prime_composite_with_large_factors(self):
        """Test that 91 (= 7*13) is correctly identified as not prime."""
        assert evaluate_pebble("(prime? 91)") is False

    def test_prime_numbers_less_than_two(self):
        """Test that 0 and 1 are not prime."""
        assert evaluate_pebble("(prime? 0)") is False
        assert evaluate_pebble("(prime? 1)") is False

    def test_prime_negative_numbers(self):
        """Test that negative numbers are not prime."""
        assert evaluate_pebble("(prime? -5)") is False


class TestPrimesUpToFunction:
    """Tests for the primes-up-to function."""

    def test_primes_up_to_less_than_two(self):
        """Test that primes-up-to returns nil for n < 2."""
        result = evaluate_pebble("(primes-up-to 1)")
        # Result should be an empty list
        result_list = list(result) if hasattr(result, '__iter__') else []
        assert len(result_list) == 0

    def test_primes_up_to_two(self):
        """Test that primes-up-to 2 returns (2)."""
        result = evaluate_pebble("(primes-up-to 2)")
        # Result should be a list-like object with 2
        result_list = list(result) if hasattr(result, '__iter__') else [result]
        assert len(result_list) == 1
        assert result_list[0] == 2

    def test_primes_up_to_ten(self):
        """Test that primes-up-to 10 returns (2 3 5 7)."""
        result = evaluate_pebble("(primes-up-to 10)")
        result_list = list(result)
        assert result_list == [2, 3, 5, 7]

    def test_primes_up_to_twenty(self):
        """Test that primes-up-to 20 returns (2 3 5 7 11 13 17 19)."""
        result = evaluate_pebble("(primes-up-to 20)")
        result_list = list(result)
        assert result_list == [2, 3, 5, 7, 11, 13, 17, 19]

    def test_primes_up_to_thirty(self):
        """Test that primes-up-to 30 returns (2 3 5 7 11 13 17 19 23 29)."""
        result = evaluate_pebble("(primes-up-to 30)")
        result_list = list(result)
        assert result_list == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    def test_primes_up_to_hundred_count(self):
        """Test that there are exactly 25 primes <= 100."""
        result = evaluate_pebble("(length (primes-up-to 100))")
        assert result == 25

    def test_primes_up_to_fifty_count(self):
        """Test that there are exactly 15 primes <= 50."""
        result = evaluate_pebble("(length (primes-up-to 50))")
        assert result == 15
