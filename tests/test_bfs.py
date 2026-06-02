"""Tests for BFS shortest-path example."""

import subprocess
import sys
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io


def test_bfs_output():
    """Test that bfs.pebble prints the expected demo output."""
    result = subprocess.run(
        [sys.executable, "-m", "pebble", "examples/bfs.pebble"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    output = result.stdout.strip()
    lines = output.split("\n")
    assert len(lines) >= 2
    assert lines[0] == "(a b d f)"
    assert lines[1] == "(a c e)"


def test_bfs_shortest_path_to_far():
    """Test shortest path from a to f."""
    code = """
    (define graph
      (make-hash
        (quote a) (list (quote b) (quote c))
        (quote b) (list (quote d))
        (quote c) (list (quote d) (quote e))
        (quote d) (list (quote f))
        (quote e) (list (quote f))
        (quote f) (list)
        (quote z) (list)))

    (define (shortest-path g start goal)
      (let loop ((queue (list start))
                 (visited (make-hash))
                 (came-from (make-hash)))
        (if (null? queue)
          nil
          (let ((current (car queue))
                (rest-queue (cdr queue)))
            (if (= current goal)
              (reconstruct-path came-from goal start)
              (if (hash-has? visited current)
                (loop rest-queue visited came-from)
                (let ((neighbors (hash-ref g current nil)))
                  (let ((new-visited (hash-set visited current true))
                        (new-queue (append rest-queue neighbors))
                        (new-came-from (mark-predecessors came-from current neighbors)))
                    (loop new-queue new-visited new-came-from)))))))))

    (define (reconstruct-path came-from goal start)
      (let loop ((current goal)
                 (path (list goal)))
        (if (= current start)
          path
          (let ((predecessor (hash-ref came-from current nil)))
            (if predecessor
              (loop predecessor (cons predecessor path))
              nil)))))

    (define (mark-predecessors came-from current neighbors)
      (if (null? neighbors)
        came-from
        (let ((neighbor (car neighbors)))
          (if (hash-has? came-from neighbor)
            (mark-predecessors came-from current (cdr neighbors))
            (let ((updated (hash-set came-from neighbor current)))
              (mark-predecessors updated current (cdr neighbors)))))))

    (shortest-path graph (quote a) (quote f))
    """

    env = make_global_env()
    result = eval_source(code, env)

    # Convert result to comparable form
    assert result is not None
    # Extract symbols from the path
    path_symbols = [str(sym) for sym in result]

    assert path_symbols == ["a", "b", "d", "f"]


def test_bfs_shortest_path_to_e():
    """Test shortest path from a to e."""
    code = """
    (define graph
      (make-hash
        (quote a) (list (quote b) (quote c))
        (quote b) (list (quote d))
        (quote c) (list (quote d) (quote e))
        (quote d) (list (quote f))
        (quote e) (list (quote f))
        (quote f) (list)
        (quote z) (list)))

    (define (shortest-path g start goal)
      (let loop ((queue (list start))
                 (visited (make-hash))
                 (came-from (make-hash)))
        (if (null? queue)
          nil
          (let ((current (car queue))
                (rest-queue (cdr queue)))
            (if (= current goal)
              (reconstruct-path came-from goal start)
              (if (hash-has? visited current)
                (loop rest-queue visited came-from)
                (let ((neighbors (hash-ref g current nil)))
                  (let ((new-visited (hash-set visited current true))
                        (new-queue (append rest-queue neighbors))
                        (new-came-from (mark-predecessors came-from current neighbors)))
                    (loop new-queue new-visited new-came-from)))))))))

    (define (reconstruct-path came-from goal start)
      (let loop ((current goal)
                 (path (list goal)))
        (if (= current start)
          path
          (let ((predecessor (hash-ref came-from current nil)))
            (if predecessor
              (loop predecessor (cons predecessor path))
              nil)))))

    (define (mark-predecessors came-from current neighbors)
      (if (null? neighbors)
        came-from
        (let ((neighbor (car neighbors)))
          (if (hash-has? came-from neighbor)
            (mark-predecessors came-from current (cdr neighbors))
            (let ((updated (hash-set came-from neighbor current)))
              (mark-predecessors updated current (cdr neighbors)))))))

    (shortest-path graph (quote a) (quote e))
    """

    env = make_global_env()
    result = eval_source(code, env)

    assert result is not None
    path_symbols = [str(sym) for sym in result]

    assert path_symbols == ["a", "c", "e"]


def test_bfs_start_equals_goal():
    """Test shortest path when start equals goal."""
    code = """
    (define graph
      (make-hash
        (quote a) (list (quote b) (quote c))
        (quote b) (list (quote d))
        (quote c) (list (quote d) (quote e))
        (quote d) (list (quote f))
        (quote e) (list (quote f))
        (quote f) (list)
        (quote z) (list)))

    (define (shortest-path g start goal)
      (let loop ((queue (list start))
                 (visited (make-hash))
                 (came-from (make-hash)))
        (if (null? queue)
          nil
          (let ((current (car queue))
                (rest-queue (cdr queue)))
            (if (= current goal)
              (reconstruct-path came-from goal start)
              (if (hash-has? visited current)
                (loop rest-queue visited came-from)
                (let ((neighbors (hash-ref g current nil)))
                  (let ((new-visited (hash-set visited current true))
                        (new-queue (append rest-queue neighbors))
                        (new-came-from (mark-predecessors came-from current neighbors)))
                    (loop new-queue new-visited new-came-from)))))))))

    (define (reconstruct-path came-from goal start)
      (let loop ((current goal)
                 (path (list goal)))
        (if (= current start)
          path
          (let ((predecessor (hash-ref came-from current nil)))
            (if predecessor
              (loop predecessor (cons predecessor path))
              nil)))))

    (define (mark-predecessors came-from current neighbors)
      (if (null? neighbors)
        came-from
        (let ((neighbor (car neighbors)))
          (if (hash-has? came-from neighbor)
            (mark-predecessors came-from current (cdr neighbors))
            (let ((updated (hash-set came-from neighbor current)))
              (mark-predecessors updated current (cdr neighbors)))))))

    (shortest-path graph (quote a) (quote a))
    """

    env = make_global_env()
    result = eval_source(code, env)

    assert result is not None
    path_symbols = [str(sym) for sym in result]

    assert path_symbols == ["a"]


def test_bfs_shortest_path_to_d():
    """Test shortest path from a to d."""
    code = """
    (define graph
      (make-hash
        (quote a) (list (quote b) (quote c))
        (quote b) (list (quote d))
        (quote c) (list (quote d) (quote e))
        (quote d) (list (quote f))
        (quote e) (list (quote f))
        (quote f) (list)
        (quote z) (list)))

    (define (shortest-path g start goal)
      (let loop ((queue (list start))
                 (visited (make-hash))
                 (came-from (make-hash)))
        (if (null? queue)
          nil
          (let ((current (car queue))
                (rest-queue (cdr queue)))
            (if (= current goal)
              (reconstruct-path came-from goal start)
              (if (hash-has? visited current)
                (loop rest-queue visited came-from)
                (let ((neighbors (hash-ref g current nil)))
                  (let ((new-visited (hash-set visited current true))
                        (new-queue (append rest-queue neighbors))
                        (new-came-from (mark-predecessors came-from current neighbors)))
                    (loop new-queue new-visited new-came-from)))))))))

    (define (reconstruct-path came-from goal start)
      (let loop ((current goal)
                 (path (list goal)))
        (if (= current start)
          path
          (let ((predecessor (hash-ref came-from current nil)))
            (if predecessor
              (loop predecessor (cons predecessor path))
              nil)))))

    (define (mark-predecessors came-from current neighbors)
      (if (null? neighbors)
        came-from
        (let ((neighbor (car neighbors)))
          (if (hash-has? came-from neighbor)
            (mark-predecessors came-from current (cdr neighbors))
            (let ((updated (hash-set came-from neighbor current)))
              (mark-predecessors updated current (cdr neighbors)))))))

    (shortest-path graph (quote a) (quote d))
    """

    env = make_global_env()
    result = eval_source(code, env)

    assert result is not None
    path_symbols = [str(sym) for sym in result]

    assert path_symbols == ["a", "b", "d"]


def test_bfs_unreachable():
    """Test shortest path when goal is unreachable."""
    code = """
    (define graph
      (make-hash
        (quote a) (list (quote b) (quote c))
        (quote b) (list (quote d))
        (quote c) (list (quote d) (quote e))
        (quote d) (list (quote f))
        (quote e) (list (quote f))
        (quote f) (list)
        (quote z) (list)))

    (define (shortest-path g start goal)
      (let loop ((queue (list start))
                 (visited (make-hash))
                 (came-from (make-hash)))
        (if (null? queue)
          nil
          (let ((current (car queue))
                (rest-queue (cdr queue)))
            (if (= current goal)
              (reconstruct-path came-from goal start)
              (if (hash-has? visited current)
                (loop rest-queue visited came-from)
                (let ((neighbors (hash-ref g current nil)))
                  (let ((new-visited (hash-set visited current true))
                        (new-queue (append rest-queue neighbors))
                        (new-came-from (mark-predecessors came-from current neighbors)))
                    (loop new-queue new-visited new-came-from)))))))))

    (define (reconstruct-path came-from goal start)
      (let loop ((current goal)
                 (path (list goal)))
        (if (= current start)
          path
          (let ((predecessor (hash-ref came-from current nil)))
            (if predecessor
              (loop predecessor (cons predecessor path))
              nil)))))

    (define (mark-predecessors came-from current neighbors)
      (if (null? neighbors)
        came-from
        (let ((neighbor (car neighbors)))
          (if (hash-has? came-from neighbor)
            (mark-predecessors came-from current (cdr neighbors))
            (let ((updated (hash-set came-from neighbor current)))
              (mark-predecessors updated current (cdr neighbors)))))))

    (shortest-path graph (quote a) (quote z))
    """

    env = make_global_env()
    result = eval_source(code, env)

    # nil should be returned for unreachable goal
    assert result is None or (hasattr(result, '__len__') and len(result) == 0)
