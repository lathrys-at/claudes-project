"""Tests for memoize higher-order function."""
import pytest
from pebble.evaluator import make_global_env, eval_source, EvalError


def eval_in_env(source, env=None):
    """Evaluate a Pebble expression and return the result."""
    if env is None:
        env = make_global_env()
    return eval_source(source, env)


class TestMemoizeCorrectness:
    """Test that memoized functions return correct values."""

    def test_memoized_square_basic(self):
        """Test basic memoized square function."""
        env = make_global_env()
        eval_in_env("(define sq (memoize (lambda (x) (* x x))))", env)
        result = eval_in_env("(sq 5)", env)
        assert result == 25

    def test_memoized_square_multiple_calls(self):
        """Test memoized square with multiple different arguments."""
        env = make_global_env()
        eval_in_env("(define sq (memoize (lambda (x) (* x x))))", env)

        result1 = eval_in_env("(sq 5)", env)
        assert result1 == 25

        result2 = eval_in_env("(sq 6)", env)
        assert result2 == 36

        result3 = eval_in_env("(sq 10)", env)
        assert result3 == 100


class TestMemoizeCaching:
    """Test that caching actually occurs."""

    def test_call_counter_caching(self):
        """Test that underlying function is called only once per argument."""
        env = make_global_env()

        # Define a call counter and memoized function that increments it
        eval_in_env("(define calls 0)", env)
        eval_in_env(
            """(define f (memoize (lambda (x)
                (begin
                  (set! calls (+ calls 1))
                  (* x x)))))""",
            env
        )

        # First call with argument 5: should call the underlying function
        result1 = eval_in_env("(f 5)", env)
        assert result1 == 25
        calls_after_first = eval_in_env("calls", env)
        assert calls_after_first == 1

        # Second call with same argument 5: should use cache, not call again
        result2 = eval_in_env("(f 5)", env)
        assert result2 == 25
        calls_after_second = eval_in_env("calls", env)
        assert calls_after_second == 1  # Still 1, cache hit

        # Call with different argument 6: should call underlying function
        result3 = eval_in_env("(f 6)", env)
        assert result3 == 36
        calls_after_third = eval_in_env("calls", env)
        assert calls_after_third == 2

        # Call with argument 5 again: should use cache
        result4 = eval_in_env("(f 5)", env)
        assert result4 == 25
        calls_after_fourth = eval_in_env("calls", env)
        assert calls_after_fourth == 2  # Still 2, cache hit


class TestMemoizedRecursion:
    """Test memoization with recursive functions."""

    def test_memoized_fib_10(self):
        """Test memoized fibonacci(10)."""
        env = make_global_env()
        eval_in_env(
            """(define fib (memoize (lambda (n)
              (if (< n 2)
                n
                (+ (fib (- n 1)) (fib (- n 2)))))))""",
            env
        )
        result = eval_in_env("(fib 10)", env)
        assert result == 55

    def test_memoized_fib_20(self):
        """Test memoized fibonacci(20)."""
        env = make_global_env()
        eval_in_env(
            """(define fib (memoize (lambda (n)
              (if (< n 2)
                n
                (+ (fib (- n 1)) (fib (- n 2)))))))""",
            env
        )
        result = eval_in_env("(fib 20)", env)
        assert result == 6765

    def test_memoized_fib_30(self):
        """Test memoized fibonacci(30) - demonstrates speedup from caching."""
        env = make_global_env()
        eval_in_env(
            """(define fib (memoize (lambda (n)
              (if (< n 2)
                n
                (+ (fib (- n 1)) (fib (- n 2)))))))""",
            env
        )
        result = eval_in_env("(fib 30)", env)
        assert result == 832040


class TestMemoizeIndependentCaches:
    """Test that different memoized functions have independent caches."""

    def test_independent_caches(self):
        """Test that multiple memoized functions maintain separate caches."""
        env = make_global_env()

        # Create two independent memoized functions
        eval_in_env("(define calls1 0)", env)
        eval_in_env("(define calls2 0)", env)

        eval_in_env(
            """(define f1 (memoize (lambda (x)
              (begin
                (set! calls1 (+ calls1 1))
                (* x x)))))""",
            env
        )

        eval_in_env(
            """(define f2 (memoize (lambda (x)
              (begin
                (set! calls2 (+ calls2 1))
                (+ x 10)))))""",
            env
        )

        # Call f1 with 5
        eval_in_env("(f1 5)", env)
        assert eval_in_env("calls1", env) == 1
        assert eval_in_env("calls2", env) == 0

        # Call f1 with 5 again (cache hit)
        eval_in_env("(f1 5)", env)
        assert eval_in_env("calls1", env) == 1
        assert eval_in_env("calls2", env) == 0

        # Call f2 with 5 (different function, should call)
        eval_in_env("(f2 5)", env)
        assert eval_in_env("calls1", env) == 1
        assert eval_in_env("calls2", env) == 1

        # Call f2 with 5 again (cache hit in f2)
        eval_in_env("(f2 5)", env)
        assert eval_in_env("calls1", env) == 1
        assert eval_in_env("calls2", env) == 1


class TestMemoizeMultipleArguments:
    """Test memoization with multiple arguments."""

    def test_multi_arg_caching(self):
        """Test that multi-arg functions use argument list as cache key."""
        env = make_global_env()

        eval_in_env("(define calls 0)", env)

        eval_in_env(
            """(define g (memoize (lambda (a b)
              (begin
                (set! calls (+ calls 1))
                (+ a b)))))""",
            env
        )

        # Call (g 2 3)
        result1 = eval_in_env("(g 2 3)", env)
        assert result1 == 5
        assert eval_in_env("calls", env) == 1

        # Call (g 2 3) again - should cache hit
        result2 = eval_in_env("(g 2 3)", env)
        assert result2 == 5
        assert eval_in_env("calls", env) == 1

        # Call (g 3 2) - different argument list, should call
        result3 = eval_in_env("(g 3 2)", env)
        assert result3 == 5  # Same result value
        assert eval_in_env("calls", env) == 2  # But underlying called again

    def test_multi_arg_different_counts(self):
        """Test that different argument counts are treated as different keys."""
        env = make_global_env()

        eval_in_env("(define calls 0)", env)

        eval_in_env(
            """(define h (memoize (lambda args
              (begin
                (set! calls (+ calls 1))
                (length args)))))""",
            env
        )

        # Call with 2 args
        result1 = eval_in_env("(h 1 2)", env)
        assert result1 == 2
        assert eval_in_env("calls", env) == 1

        # Call with 2 args again
        result2 = eval_in_env("(h 1 2)", env)
        assert result2 == 2
        assert eval_in_env("calls", env) == 1  # Cache hit

        # Call with 3 args - different cache key
        result3 = eval_in_env("(h 1 2 3)", env)
        assert result3 == 3
        assert eval_in_env("calls", env) == 2
