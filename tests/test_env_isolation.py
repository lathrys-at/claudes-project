"""Tests for environment isolation and prelude availability.

These tests verify that:
1. Environments returned by make_global_env() are isolated from each other
2. Defines in one environment do not leak to another
3. Redefinitions in one environment do not affect another
4. set! in one environment does not affect another
5. The prelude is fully available in each environment
"""
import pytest
from pebble.evaluator import make_global_env, seval, EvalError
from pebble.reader import read
from pebble.types import PebbleList


class TestEnvIsolation:
    """Test that environments are properly isolated."""

    def test_defines_do_not_leak_between_envs(self):
        """Test that defining a name in env A doesn't affect env B."""
        env_a = make_global_env()
        env_b = make_global_env()

        # Define 'foo' in env_a
        seval(read("(define foo 1)")[0], env_a)

        # Verify foo is 1 in env_a
        result_a = seval(read("foo")[0], env_a)
        assert result_a == 1

        # Verify foo is undefined in env_b
        with pytest.raises(EvalError, match="undefined symbol"):
            seval(read("foo")[0], env_b)

    def test_redefining_prelude_function_does_not_leak(self):
        """Test that redefining a prelude function in env A doesn't affect env B."""
        env_a = make_global_env()
        env_b = make_global_env()

        # Redefine 'inc' in env_a to add 100 instead of 1
        seval(read("(define inc (lambda (n) (+ n 100)))")[0], env_a)

        # Verify new definition in env_a
        result_a = seval(read("(inc 5)")[0], env_a)
        assert result_a == 105

        # Verify original definition still in env_b
        result_b = seval(read("(inc 5)")[0], env_b)
        assert result_b == 6

    def test_set_does_not_leak_between_envs(self):
        """Test that set! in env A doesn't affect env B."""
        env_a = make_global_env()
        env_b = make_global_env()

        # Define counter in env_a and set it
        seval(read("(define counter 0)")[0], env_a)
        seval(read("(set! counter 5)")[0], env_a)

        # Verify counter is 5 in env_a
        result_a = seval(read("counter")[0], env_a)
        assert result_a == 5

        # Verify counter doesn't exist in env_b
        with pytest.raises(EvalError, match="undefined symbol"):
            seval(read("counter")[0], env_b)

    def test_prelude_functions_available(self):
        """Test that stdlib functions from the prelude are available."""
        env = make_global_env()

        # Test map function
        result = seval(
            read("(map (lambda (x) (* x x)) (list 1 2 3))")[0],
            env
        )
        assert isinstance(result, PebbleList)
        assert list(result) == [1, 4, 9]

    def test_prelude_macros_available(self):
        """Test that stdlib macros from the prelude are available."""
        env = make_global_env()

        # Test 'when' macro with true condition
        result = seval(
            read("(when true 42)")[0],
            env
        )
        assert result == 42

        # Test 'when' with false condition
        result = seval(
            read("(when false 42)")[0],
            env
        )
        # when should return the value of the body or NIL
        assert result is not None  # Should be NIL or similar

    def test_multiple_independent_sessions(self):
        """Test that multiple independent sessions can coexist."""
        env_a = make_global_env()
        env_b = make_global_env()
        env_c = make_global_env()

        # Define different things in each
        seval(read("(define x 1)")[0], env_a)
        seval(read("(define x 2)")[0], env_b)
        seval(read("(define x 3)")[0], env_c)

        # Verify each sees its own value
        assert seval(read("x")[0], env_a) == 1
        assert seval(read("x")[0], env_b) == 2
        assert seval(read("x")[0], env_c) == 3

    def test_prelude_not_loaded_when_load_prelude_false(self):
        """Test that load_prelude=False doesn't include prelude definitions."""
        env = make_global_env(load_prelude=False)

        # Builtins like + should exist
        result = seval(read("(+ 1 2)")[0], env)
        assert result == 3

        # But prelude macros like 'when' should not exist
        with pytest.raises(EvalError, match="undefined symbol"):
            seval(read("(when true 42)")[0], env)

    def test_builtins_available_in_all_envs(self):
        """Test that primitive builtins are always available."""
        env_with_prelude = make_global_env(load_prelude=True)
        env_without_prelude = make_global_env(load_prelude=False)

        # Both should have +
        result1 = seval(read("(+ 1 2)")[0], env_with_prelude)
        result2 = seval(read("(+ 1 2)")[0], env_without_prelude)
        assert result1 == 3
        assert result2 == 3

        # Both should have list
        result1 = seval(read("(list 1 2)")[0], env_with_prelude)
        result2 = seval(read("(list 1 2)")[0], env_without_prelude)
        assert isinstance(result1, PebbleList)
        assert isinstance(result2, PebbleList)
