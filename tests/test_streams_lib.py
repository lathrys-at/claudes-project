"""Tests for lazy streams library in the prelude built on delay/force."""
import pytest
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList


class TestStreamsCons:
    """Tests for stream-cons macro."""

    def test_stream_cons_creates_list_with_promise(self):
        """Test that stream-cons creates a two-element list (list HEAD (delay REST))."""
        env = make_global_env()
        # stream-cons should create a delayed stream
        code = "(stream-cons 1 nil)"
        result = eval_source(code, env)
        # Result should be a list with 1 as head and a promise as tail
        assert len(result) == 2
        assert result[0] == 1
        # The second element should be a promise
        # We verify the structure is correct by testing stream operations
        assert eval_source("(stream-car (stream-cons 1 nil))", env) == 1

    def test_stream_cons_delays_tail(self):
        """Test that stream-cons macro delays the TAIL evaluation."""
        env = make_global_env()
        # If stream-cons weren't a macro, this would hang (integers-from 2 evaluated eagerly)
        code = "(stream-take (stream-cons 1 (integers-from 2)) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((1, 2, 3))


class TestStreamCar:
    """Tests for stream-car function."""

    def test_stream_car_returns_head(self):
        """Test that stream-car returns the head element."""
        env = make_global_env()
        code = "(stream-car (stream-cons 5 nil))"
        result = eval_source(code, env)
        assert result == 5

    def test_stream_car_from_integers(self):
        """Test (stream-car (integers-from 7)) -> 7."""
        env = make_global_env()
        code = "(stream-car (integers-from 7))"
        result = eval_source(code, env)
        assert result == 7


class TestStreamCdr:
    """Tests for stream-cdr function."""

    def test_stream_cdr_returns_rest(self):
        """Test that stream-cdr forces and returns the rest of the stream."""
        env = make_global_env()
        code = "(stream-car (stream-cdr (integers-from 7)))"
        result = eval_source(code, env)
        assert result == 8

    def test_stream_cdr_forces_lazy_tail(self):
        """Test that stream-cdr forces the delayed tail."""
        env = make_global_env()
        code = "(let* ((s (stream-cons 1 (stream-cons 2 nil))) (rest (stream-cdr s))) (stream-car rest))"
        result = eval_source(code, env)
        assert result == 2


class TestStreamNull:
    """Tests for stream-null? predicate."""

    def test_stream_null_empty_list(self):
        """Test (stream-null? nil) -> true."""
        env = make_global_env()
        code = "(stream-null? nil)"
        result = eval_source(code, env)
        assert result is True

    def test_stream_null_infinite_stream(self):
        """Test (stream-null? (integers-from 1)) -> false."""
        env = make_global_env()
        code = "(stream-null? (integers-from 1))"
        result = eval_source(code, env)
        assert result is False

    def test_stream_null_finite_stream(self):
        """Test (stream-null? (stream-cons 1 (stream-cons 2 nil))) -> false."""
        env = make_global_env()
        code = "(stream-null? (stream-cons 1 (stream-cons 2 nil)))"
        result = eval_source(code, env)
        assert result is False


class TestStreamTake:
    """Tests for stream-take function."""

    def test_stream_take_from_integers_from_1(self):
        """Test (stream-take (integers-from 1) 5) -> (1 2 3 4 5)."""
        env = make_global_env()
        code = "(stream-take (integers-from 1) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((1, 2, 3, 4, 5))

    def test_stream_take_from_integers_from_10(self):
        """Test (stream-take (integers-from 10) 3) -> (10 11 12)."""
        env = make_global_env()
        code = "(stream-take (integers-from 10) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((10, 11, 12))

    def test_stream_take_0(self):
        """Test (stream-take s 0) returns the empty list."""
        env = make_global_env()
        code = "(stream-take (integers-from 1) 0)"
        result = eval_source(code, env)
        assert result == PebbleList(())

    def test_stream_take_from_finite_stream(self):
        """Test taking more than available from a finite stream.

        (stream-take (stream-cons 1 (stream-cons 2 nil)) 5) -> (1 2)
        """
        env = make_global_env()
        code = "(stream-take (stream-cons 1 (stream-cons 2 nil)) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((1, 2))

    def test_stream_take_from_empty_stream(self):
        """Test (stream-take nil 5) -> nil."""
        env = make_global_env()
        code = "(stream-take nil 5)"
        result = eval_source(code, env)
        assert result == PebbleList(())

    def test_stream_take_large_number_terminates(self):
        """Test that (stream-take (integers-from 1) 100) terminates (laziness proof).

        This would hang forever if streams were not lazy.
        """
        env = make_global_env()
        code = "(stream-take (integers-from 1) 100)"
        result = eval_source(code, env)
        # Verify it actually produced 100 elements
        assert len(result) == 100
        assert result[0] == 1
        assert result[99] == 100


class TestStreamRef:
    """Tests for stream-ref function."""

    def test_stream_ref_0_indexed(self):
        """Test (stream-ref (integers-from 10) 3) -> 13."""
        env = make_global_env()
        code = "(stream-ref (integers-from 10) 3)"
        result = eval_source(code, env)
        assert result == 13

    def test_stream_ref_first_element(self):
        """Test (stream-ref (integers-from 5) 0) -> 5."""
        env = make_global_env()
        code = "(stream-ref (integers-from 5) 0)"
        result = eval_source(code, env)
        assert result == 5

    def test_stream_ref_various_indices(self):
        """Test stream-ref with various indices."""
        env = make_global_env()
        for i, expected in enumerate([100, 101, 102, 103, 104]):
            code = f"(stream-ref (integers-from 100) {i})"
            result = eval_source(code, env)
            assert result == expected


class TestStreamMap:
    """Tests for stream-map function."""

    def test_stream_map_squares(self):
        """Test (stream-take (stream-map (lambda (x) (* x x)) (integers-from 1)) 5) -> (1 4 9 16 25)."""
        env = make_global_env()
        code = "(stream-take (stream-map (lambda (x) (* x x)) (integers-from 1)) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((1, 4, 9, 16, 25))

    def test_stream_map_multiply_by_10(self):
        """Test (stream-take (stream-map (lambda (x) (* x 10)) (integers-from 1)) 3) -> (10 20 30)."""
        env = make_global_env()
        code = "(stream-take (stream-map (lambda (x) (* x 10)) (integers-from 1)) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((10, 20, 30))

    def test_stream_map_on_empty_stream(self):
        """Test (stream-map f nil) -> nil."""
        env = make_global_env()
        code = "(stream-map (lambda (x) (* x 2)) nil)"
        result = eval_source(code, env)
        assert result == PebbleList(())

    def test_stream_map_laziness(self):
        """Test that stream-map is lazy (doesn't evaluate function until elements are accessed)."""
        env = make_global_env()
        # This should not hang even though we map over an infinite stream
        code = "(stream-take (stream-map (lambda (x) (* x x)) (integers-from 1)) 10)"
        result = eval_source(code, env)
        assert len(result) == 10
        assert result[0] == 1
        assert result[9] == 100


class TestStreamFilter:
    """Tests for stream-filter function."""

    def test_stream_filter_even_numbers(self):
        """Test (stream-take (stream-filter even? (integers-from 1)) 4) -> (2 4 6 8)."""
        env = make_global_env()
        code = "(stream-take (stream-filter even? (integers-from 1)) 4)"
        result = eval_source(code, env)
        assert result == PebbleList((2, 4, 6, 8))

    def test_stream_filter_odd_numbers(self):
        """Test (stream-take (stream-filter odd? (integers-from 1)) 4) -> (1 3 5 7)."""
        env = make_global_env()
        code = "(stream-take (stream-filter odd? (integers-from 1)) 4)"
        result = eval_source(code, env)
        assert result == PebbleList((1, 3, 5, 7))

    def test_stream_filter_greater_than_5(self):
        """Test (stream-take (stream-filter (lambda (x) (> x 5)) (integers-from 1)) 3) -> (6 7 8)."""
        env = make_global_env()
        code = "(stream-take (stream-filter (lambda (x) (> x 5)) (integers-from 1)) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((6, 7, 8))

    def test_stream_filter_on_empty_stream(self):
        """Test (stream-filter pred nil) -> nil."""
        env = make_global_env()
        code = "(stream-filter even? nil)"
        result = eval_source(code, env)
        assert result == PebbleList(())

    def test_stream_filter_laziness(self):
        """Test that stream-filter is lazy (doesn't evaluate all elements)."""
        env = make_global_env()
        # This should terminate even though we filter an infinite stream
        code = "(stream-take (stream-filter even? (integers-from 1)) 50)"
        result = eval_source(code, env)
        assert len(result) == 50
        assert result[0] == 2
        assert result[49] == 100


class TestStreamZipWith:
    """Tests for stream-zip-with function."""

    def test_stream_zip_with_addition(self):
        """Test (stream-take (stream-zip-with + (integers-from 1) (integers-from 100)) 3) -> (101 103 105)."""
        env = make_global_env()
        code = "(stream-take (stream-zip-with + (integers-from 1) (integers-from 100)) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((101, 103, 105))

    def test_stream_zip_with_multiplication(self):
        """Test (stream-take (stream-zip-with * (integers-from 1) (integers-from 10)) 3) -> (10 22 36).

        integers-from 1 produces (1, 2, 3, ...)
        integers-from 10 produces (10, 11, 12, ...)
        zip with * produces (1*10, 2*11, 3*12, ...) = (10, 22, 36, ...)
        """
        env = make_global_env()
        code = "(stream-take (stream-zip-with * (integers-from 1) (integers-from 10)) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((10, 22, 36))

    def test_stream_zip_with_stops_at_shorter_stream(self):
        """Test that stream-zip-with stops when either stream is empty.

        Zip a finite 2-element stream with an infinite stream.
        Finite stream: (1, 2)
        Infinite stream: (100, 101, 102, ...)
        Result: (1+100, 2+101) = (101, 103), then stops
        """
        env = make_global_env()
        code = "(stream-zip-with + (stream-cons 1 (stream-cons 2 nil)) (integers-from 100))"
        result = eval_source(code, env)
        # The result is a stream; take its first 5 elements (but there are only 2)
        taken = eval_source("(stream-take (stream-zip-with + (stream-cons 1 (stream-cons 2 nil)) (integers-from 100)) 5)", env)
        assert taken == PebbleList((101, 103))

    def test_stream_zip_with_both_finite(self):
        """Test zipping two finite streams."""
        env = make_global_env()
        code = "(stream-zip-with + (stream-cons 1 (stream-cons 2 (stream-cons 3 nil))) (stream-cons 10 (stream-cons 20 (stream-cons 30 nil))))"
        result = eval_source(code, env)
        taken = eval_source("(stream-take (stream-zip-with + (stream-cons 1 (stream-cons 2 (stream-cons 3 nil))) (stream-cons 10 (stream-cons 20 (stream-cons 30 nil)))) 10)", env)
        assert taken == PebbleList((11, 22, 33))

    def test_stream_zip_with_empty_stream(self):
        """Test (stream-zip-with f nil s2) -> nil."""
        env = make_global_env()
        code = "(stream-zip-with + nil (integers-from 1))"
        result = eval_source(code, env)
        assert result == PebbleList(())


class TestIntegersFrom:
    """Tests for integers-from function."""

    def test_integers_from_1(self):
        """Test (stream-take (integers-from 1) 5) -> (1 2 3 4 5)."""
        env = make_global_env()
        code = "(stream-take (integers-from 1) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((1, 2, 3, 4, 5))

    def test_integers_from_0(self):
        """Test (stream-take (integers-from 0) 5) -> (0 1 2 3 4)."""
        env = make_global_env()
        code = "(stream-take (integers-from 0) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((0, 1, 2, 3, 4))

    def test_integers_from_negative(self):
        """Test (stream-take (integers-from -2) 5) -> (-2 -1 0 1 2)."""
        env = make_global_env()
        code = "(stream-take (integers-from -2) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((-2, -1, 0, 1, 2))

    def test_integers_from_is_infinite(self):
        """Test that integers-from is truly infinite (can take arbitrarily many elements)."""
        env = make_global_env()
        code = "(stream-take (integers-from 1000000) 5)"
        result = eval_source(code, env)
        assert result == PebbleList((1000000, 1000001, 1000002, 1000003, 1000004))


class TestComplexCompositions:
    """Tests for complex combinations of stream operations."""

    def test_map_then_filter(self):
        """Test composing stream-map and stream-filter.

        Take first 3 even numbers from doubled integers.
        (stream-take (stream-filter even? (stream-map (lambda (x) (* x 2)) (integers-from 1))) 3) -> (2 4 6)
        """
        env = make_global_env()
        code = "(stream-take (stream-filter even? (stream-map (lambda (x) (* x 2)) (integers-from 1))) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((2, 4, 6))

    def test_filter_then_map(self):
        """Test composing stream-filter and stream-map.

        (stream-take (stream-map (lambda (x) (* x 10)) (stream-filter odd? (integers-from 1))) 3) -> (10 30 50)
        """
        env = make_global_env()
        code = "(stream-take (stream-map (lambda (x) (* x 10)) (stream-filter odd? (integers-from 1))) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((10, 30, 50))

    def test_map_zip_map(self):
        """Test composing multiple operations: map a zipped result.

        (stream-take (stream-map (lambda (x) (+ x 1000)) (stream-zip-with + (integers-from 1) (integers-from 1))) 3) -> (1002 1004 1006)
        """
        env = make_global_env()
        code = "(stream-take (stream-map (lambda (x) (+ x 1000)) (stream-zip-with + (integers-from 1) (integers-from 1))) 3)"
        result = eval_source(code, env)
        assert result == PebbleList((1002, 1004, 1006))

    def test_deeply_nested_streams(self):
        """Test a deeply nested composition of operations."""
        env = make_global_env()
        # Take 3 elements from: filter odd, map *2, zip sum, filter >10, integers-from 1
        code = """(stream-take
            (stream-filter
              (lambda (x) (> x 10))
              (stream-zip-with +
                (stream-map (lambda (x) (* x 2)) (integers-from 1))
                (integers-from 100)))
            3)"""
        result = eval_source(code, env)
        # First stream: 2, 4, 6, 8, 10, 12, 14, ...
        # Second stream: 100, 101, 102, 103, ...
        # Zipped: 102, 105, 108, 111, 114, 117, ...
        # Filtered > 10: 102, 105, 108, 111, 114, 117, ...
        # Take 3: (102, 105, 108)
        assert result == PebbleList((102, 105, 108))
