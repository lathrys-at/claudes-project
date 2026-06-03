"""Tests for the immutable FIFO queue example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


@pytest.fixture(scope="module")
def queue_env_and_output():
    """Load the queue.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "queue.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestQueue:
    """Tests for the immutable FIFO queue implementation."""

    def test_example_output(self, queue_env_and_output):
        """Test that the example file produces the correct output: (1 2 3)."""
        env, demo_output = queue_env_and_output

        # The demo should print exactly "(1 2 3)" followed by a newline
        assert demo_output.strip() == "(1 2 3)"

    def test_make_queue(self, queue_env_and_output):
        """Test that make-queue returns an empty queue."""
        env, _ = queue_env_and_output

        q = eval_source("(make-queue)", env)
        # Queue is represented as (nil nil)
        assert isinstance(q, PebbleList)
        assert len(q) == 2
        # In Pebble, nil is represented as an empty PebbleList
        assert q[0] == PebbleList([])  # front is nil
        assert q[1] == PebbleList([])  # back is nil

    def test_queue_empty_on_new_queue(self, queue_env_and_output):
        """Test that queue-empty? returns true for a new queue."""
        env, _ = queue_env_and_output

        result = eval_source("(queue-empty? (make-queue))", env)
        assert result is True

    def test_queue_empty_after_enqueue(self, queue_env_and_output):
        """Test that queue-empty? returns false after enqueuing."""
        env, _ = queue_env_and_output

        result = eval_source("(queue-empty? (enqueue (make-queue) 1))", env)
        assert result is False

    def test_queue_to_list_empty(self, queue_env_and_output):
        """Test that queue->list returns nil for an empty queue."""
        env, _ = queue_env_and_output

        result = eval_source("(queue->list (make-queue))", env)
        # In Pebble, nil is represented as an empty PebbleList
        assert result == PebbleList([])

    def test_queue_to_list_single_element(self, queue_env_and_output):
        """Test queue->list with a single enqueued element."""
        env, _ = queue_env_and_output

        result = eval_source("(queue->list (enqueue (make-queue) 1))", env)
        assert isinstance(result, PebbleList)
        assert len(result) == 1
        assert result[0] == 1

    def test_queue_to_list_fifo_order(self, queue_env_and_output):
        """Test that queue->list returns elements in FIFO order."""
        env, _ = queue_env_and_output

        result = eval_source(
            "(queue->list (enqueue (enqueue (enqueue (make-queue) 1) 2) 3))",
            env
        )
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 3

    def test_queue_size_empty(self, queue_env_and_output):
        """Test queue-size returns 0 for an empty queue."""
        env, _ = queue_env_and_output

        result = eval_source("(queue-size (make-queue))", env)
        assert result == 0

    def test_queue_size_two_elements(self, queue_env_and_output):
        """Test queue-size returns correct count."""
        env, _ = queue_env_and_output

        result = eval_source("(queue-size (enqueue (enqueue (make-queue) 1) 2))", env)
        assert result == 2

    def test_queue_size_three_elements(self, queue_env_and_output):
        """Test queue-size with three enqueued elements."""
        env, _ = queue_env_and_output

        result = eval_source(
            "(queue-size (enqueue (enqueue (enqueue (make-queue) 1) 2) 3))",
            env
        )
        assert result == 3

    def test_dequeue_returns_pair(self, queue_env_and_output):
        """Test that dequeue returns a two-element list (value new-queue)."""
        env, _ = queue_env_and_output

        result = eval_source(
            "(dequeue (enqueue (make-queue) 42))",
            env
        )
        assert isinstance(result, PebbleList)
        assert len(result) == 2

    def test_dequeue_value_first_element(self, queue_env_and_output):
        """Test that dequeue returns the correct value for a single-element queue."""
        env, _ = queue_env_and_output

        result = eval_source(
            "(car (dequeue (enqueue (make-queue) 42)))",
            env
        )
        assert result == 42

    def test_dequeue_fifo_order_sequence(self, queue_env_and_output):
        """Test FIFO dequeue order: enqueue 1, 2, 3; dequeue yields 1, 2, 3."""
        env, _ = queue_env_and_output

        # Create queue with 1, 2, 3
        setup = "(define q (enqueue (enqueue (enqueue (make-queue) 1) 2) 3))"
        eval_source(setup, env)

        # Dequeue 1
        r1_result = eval_source("(define r1 (dequeue q))", env)
        v1 = eval_source("(car r1)", env)
        assert v1 == 1

        # Dequeue 2 from the queue in r1
        r2_result = eval_source("(define r2 (dequeue (cadr r1)))", env)
        v2 = eval_source("(car r2)", env)
        assert v2 == 2

        # Dequeue 3 from the queue in r2
        r3_result = eval_source("(define r3 (dequeue (cadr r2)))", env)
        v3 = eval_source("(car r3)", env)
        assert v3 == 3

    def test_dequeue_empty_raises_error(self, queue_env_and_output):
        """Test that dequeue on an empty queue raises an error."""
        env, _ = queue_env_and_output

        with pytest.raises(Exception) as exc_info:
            eval_source("(dequeue (make-queue))", env)
        assert "dequeue: empty queue" in str(exc_info.value)

    def test_mixed_operations_fifo(self, queue_env_and_output):
        """Test mixed enqueue/dequeue operations.

        Enqueue 1 and 2, dequeue once (removing 1), enqueue 3 and 4,
        then verify queue->list yields (2 3 4).
        """
        env, _ = queue_env_and_output

        code = """
        (let ((q1 (enqueue (enqueue (make-queue) 1) 2)))
          (let ((r1 (dequeue q1)))
            (let ((q2 (cadr r1)))
              (let ((q3 (enqueue (enqueue q2 3) 4)))
                (queue->list q3)))))
        """
        result = eval_source(code, env)
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == 2
        assert result[1] == 3
        assert result[2] == 4

    def test_immutability_enqueue_does_not_modify_original(self, queue_env_and_output):
        """Test that enqueue does not modify the original queue."""
        env, _ = queue_env_and_output

        code = """
        (let ((q1 (enqueue (enqueue (make-queue) 1) 2)))
          (let ((q2 (enqueue q1 3)))
            (list (queue->list q1) (queue->list q2))))
        """
        result = eval_source(code, env)
        assert isinstance(result, PebbleList)

        # q1 should still be (1 2)
        q1_list = result[0]
        assert isinstance(q1_list, PebbleList)
        assert len(q1_list) == 2
        assert q1_list[0] == 1
        assert q1_list[1] == 2

        # q2 should be (1 2 3)
        q2_list = result[1]
        assert isinstance(q2_list, PebbleList)
        assert len(q2_list) == 3
        assert q2_list[0] == 1
        assert q2_list[1] == 2
        assert q2_list[2] == 3

    def test_immutability_dequeue_does_not_modify_original(self, queue_env_and_output):
        """Test that dequeue does not modify the original queue."""
        env, _ = queue_env_and_output

        code = """
        (let ((q1 (enqueue (enqueue (enqueue (make-queue) 1) 2) 3)))
          (let ((r (dequeue q1)))
            (let ((q2 (cadr r)))
              (list (queue->list q1) (queue->list q2)))))
        """
        result = eval_source(code, env)
        assert isinstance(result, PebbleList)

        # q1 should still be (1 2 3)
        q1_list = result[0]
        assert isinstance(q1_list, PebbleList)
        assert len(q1_list) == 3
        assert q1_list[0] == 1
        assert q1_list[1] == 2
        assert q1_list[2] == 3

        # q2 should be (2 3)
        q2_list = result[1]
        assert isinstance(q2_list, PebbleList)
        assert len(q2_list) == 2
        assert q2_list[0] == 2
        assert q2_list[1] == 3

    def test_front_empty_back_nonempty_dequeue(self, queue_env_and_output):
        """Test dequeue when front is empty but back is non-empty.

        This exercises the banker's queue's rebalancing: when the front
        becomes empty during dequeue, the reversed back becomes the new front.
        """
        env, _ = queue_env_and_output

        # Enqueue 1, 2, 3 (1 goes to front, 2 and 3 accumulate in back in reverse)
        # Dequeue removes 1 from front, leaving front empty but back with (3 2)
        # The next dequeue should reverse back to get (2 3) and take 2
        code = """
        (let ((q1 (enqueue (enqueue (enqueue (make-queue) 1) 2) 3)))
          (let ((r1 (dequeue q1)))
            (let ((q2 (cadr r1)))
              (let ((r2 (dequeue q2)))
                (let ((val2 (car r2)))
                  val2)))))
        """
        result = eval_source(code, env)
        assert result == 2

    def test_queue_with_various_types(self, queue_env_and_output):
        """Test that queues can hold various data types."""
        env, _ = queue_env_and_output

        code = """
        (queue->list (enqueue (enqueue (enqueue (make-queue) "hello") 42) true))
        """
        result = eval_source(code, env)
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == "hello"
        assert result[1] == 42
        assert result[2] is True

    def test_enqueue_multiple_times_increases_size(self, queue_env_and_output):
        """Test that each enqueue increases queue size by 1."""
        env, _ = queue_env_and_output

        # Size progression: 0 -> 1 -> 2 -> 3 -> 4 -> 5
        code = """
        (list
          (queue-size (make-queue))
          (queue-size (enqueue (make-queue) 1))
          (queue-size (enqueue (enqueue (make-queue) 1) 2))
          (queue-size (enqueue (enqueue (enqueue (make-queue) 1) 2) 3))
          (queue-size (enqueue (enqueue (enqueue (enqueue (make-queue) 1) 2) 3) 4))
          (queue-size (enqueue (enqueue (enqueue (enqueue (enqueue (make-queue) 1) 2) 3) 4) 5)))
        """
        result = eval_source(code, env)
        assert isinstance(result, PebbleList)
        assert len(result) == 6
        assert result[0] == 0
        assert result[1] == 1
        assert result[2] == 2
        assert result[3] == 3
        assert result[4] == 4
        assert result[5] == 5
