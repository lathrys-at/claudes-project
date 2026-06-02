"""Tests for the binary min-heap example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


@pytest.fixture(scope="module")
def heap_env_and_output():
    """Load the heap.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "heap.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestHeap:
    """Tests for the binary min-heap implementation."""

    def test_demo_output(self, heap_env_and_output):
        """Test that the example file produces the correct demo output."""
        env, demo_output = heap_env_and_output
        expected_output = "(1 2 3 5 7 8 9)\n"
        assert demo_output == expected_output

    def test_heapsort_basic(self, heap_env_and_output):
        """Test heapsort with the standard example."""
        env, _ = heap_env_and_output
        result = eval_source("(heapsort (list 5 3 8 1 9 2 7))", env)
        expected = eval_source("(list 1 2 3 5 7 8 9)", env)
        assert result == expected

    def test_heapsort_empty_list(self, heap_env_and_output):
        """Test heapsort on empty list."""
        env, _ = heap_env_and_output
        result = eval_source("(heapsort (list))", env)
        assert result == eval_source("nil", env)

    def test_heapsort_single_element(self, heap_env_and_output):
        """Test heapsort on single element."""
        env, _ = heap_env_and_output
        result = eval_source("(heapsort (list 1))", env)
        expected = eval_source("(list 1)", env)
        assert result == expected

    def test_heapsort_three_elements(self, heap_env_and_output):
        """Test heapsort on three elements."""
        env, _ = heap_env_and_output
        result = eval_source("(heapsort (list 3 1 2))", env)
        expected = eval_source("(list 1 2 3)", env)
        assert result == expected

    def test_heapsort_with_duplicates(self, heap_env_and_output):
        """Test heapsort preserves duplicates."""
        env, _ = heap_env_and_output
        result = eval_source("(heapsort (list 3 1 2 1 3))", env)
        expected = eval_source("(list 1 1 2 3 3)", env)
        assert result == expected

    def test_heapsort_larger_case(self, heap_env_and_output):
        """Test heapsort on larger descending sequence."""
        env, _ = heap_env_and_output
        result = eval_source("(heapsort (list 10 9 8 7 6 5 4 3 2 1))", env)
        expected = eval_source("(list 1 2 3 4 5 6 7 8 9 10)", env)
        assert result == expected

    def test_make_heap_empty(self, heap_env_and_output):
        """Test that make-heap creates an empty heap."""
        env, _ = heap_env_and_output
        result = eval_source("(define h (make-heap)) (heap-empty? h)", env)
        assert result is True

    def test_heap_size_after_insert(self, heap_env_and_output):
        """Test heap size after insertions."""
        env, _ = heap_env_and_output
        result = eval_source(
            "(define h (make-heap)) "
            "(heap-insert! h 5) "
            "(heap-insert! h 3) "
            "(heap-insert! h 8) "
            "(heap-insert! h 1) "
            "(heap-size h)",
            env
        )
        assert result == 4

    def test_heap_peek_min(self, heap_env_and_output):
        """Test that peek-min returns the minimum without removing it."""
        env, _ = heap_env_and_output
        result = eval_source(
            "(define h (make-heap)) "
            "(heap-insert! h 5) "
            "(heap-insert! h 3) "
            "(heap-insert! h 8) "
            "(heap-insert! h 1) "
            "(heap-peek-min h)",
            env
        )
        assert result == 1

    def test_heap_peek_min_preserves_size(self, heap_env_and_output):
        """Test that peek-min does not change heap size."""
        env, _ = heap_env_and_output
        result = eval_source(
            "(define h (make-heap)) "
            "(heap-insert! h 5) "
            "(heap-insert! h 3) "
            "(heap-insert! h 8) "
            "(heap-insert! h 1) "
            "(heap-peek-min h) "
            "(heap-size h)",
            env
        )
        assert result == 4

    def test_heap_pop_min_sequence(self, heap_env_and_output):
        """Test popping elements in order."""
        env, _ = heap_env_and_output
        result1 = eval_source(
            "(define h (make-heap)) "
            "(heap-insert! h 5) "
            "(heap-insert! h 3) "
            "(heap-insert! h 8) "
            "(heap-insert! h 1) "
            "(heap-pop-min! h)",
            env
        )
        assert result1 == 1

        result2 = eval_source("(heap-pop-min! h)", env)
        assert result2 == 3

        result3 = eval_source("(heap-pop-min! h)", env)
        assert result3 == 5

        result4 = eval_source("(heap-pop-min! h)", env)
        assert result4 == 8

    def test_heap_empty_after_all_pops(self, heap_env_and_output):
        """Test that heap is empty after popping all elements."""
        env, _ = heap_env_and_output
        eval_source(
            "(define h (make-heap)) "
            "(heap-insert! h 5) "
            "(heap-insert! h 3) "
            "(heap-insert! h 8) "
            "(heap-insert! h 1) "
            "(heap-pop-min! h) "
            "(heap-pop-min! h) "
            "(heap-pop-min! h) "
            "(heap-pop-min! h)",
            env
        )
        result = eval_source("(heap-empty? h)", env)
        assert result is True

    def test_heap_pop_min_empty_raises_error(self, heap_env_and_output):
        """Test that popping from empty heap raises EvalError."""
        env, _ = heap_env_and_output
        with pytest.raises(Exception):
            eval_source("(heap-pop-min! (make-heap))", env)

    def test_heap_peek_min_empty_raises_error(self, heap_env_and_output):
        """Test that peeking at empty heap raises EvalError."""
        env, _ = heap_env_and_output
        with pytest.raises(Exception):
            eval_source("(heap-peek-min (make-heap))", env)
