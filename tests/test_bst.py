"""Tests for the immutable binary search tree example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


def _load_bst_example():
    """Helper function to load bst.pebble and capture its output."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "bst.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def bst_env_and_output():
    """Load bst.pebble once and capture its output."""
    return _load_bst_example()


class TestBinarySearchTree:
    """Tests for the immutable BST example program."""

    def test_demo_output(self, bst_env_and_output):
        """Test that the BST example produces the correct demo output."""
        env, demo_output = bst_env_and_output

        expected_lines = [
            "(1 2 3 4 5 7 8 9)",
            "true",
            "false"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_inorder_sorted(self, bst_env_and_output):
        """Test that tree-inorder returns values in sorted order."""
        env, demo_output = bst_env_and_output

        code = "(tree-inorder (tree-from-list (list 5 3 8 1 4 7 9 2)))"
        result = eval_source(code, env)
        assert result == PebbleList((1, 2, 3, 4, 5, 7, 8, 9))

    def test_inorder_duplicates_ignored(self, bst_env_and_output):
        """Test that duplicates are ignored in the BST."""
        env, demo_output = bst_env_and_output

        code = "(tree-inorder (tree-from-list (list 3 3 3)))"
        result = eval_source(code, env)
        assert result == PebbleList((3,))

    def test_inorder_empty_tree(self, bst_env_and_output):
        """Test that inorder of empty tree yields empty list."""
        env, demo_output = bst_env_and_output

        code = "(tree-inorder (tree-from-list (list)))"
        result = eval_source(code, env)
        assert result == PebbleList(())

    def test_contains_present(self, bst_env_and_output):
        """Test that tree-contains? returns true for present value."""
        env, demo_output = bst_env_and_output

        code = "(tree-contains? (tree-from-list (list 5 3 8)) 3)"
        result = eval_source(code, env)
        assert result is True

    def test_contains_absent(self, bst_env_and_output):
        """Test that tree-contains? returns false for absent value."""
        env, demo_output = bst_env_and_output

        code = "(tree-contains? (tree-from-list (list 5 3 8)) 6)"
        result = eval_source(code, env)
        assert result is False

    def test_contains_empty_tree(self, bst_env_and_output):
        """Test that tree-contains? returns false for empty tree."""
        env, demo_output = bst_env_and_output

        code = "(tree-contains? nil 5)"
        result = eval_source(code, env)
        assert result is False

    def test_immutability_insert(self, bst_env_and_output):
        """Test that tree-insert does not mutate the original tree."""
        env, demo_output = bst_env_and_output

        code = """
        (define t1 (tree-from-list (list 5 3 8)))
        (define inorder-before (tree-inorder t1))
        (define t2 (tree-insert t1 7))
        (define inorder-after (tree-inorder t1))
        (and (= inorder-before inorder-after) (> (length (tree-inorder t2)) (length (tree-inorder t1))))
        """
        result = eval_source(code, env)
        assert result is True

    def test_node_record_type(self, bst_env_and_output):
        """Test that nodes use the define-record generated constructor and accessors."""
        env, demo_output = bst_env_and_output

        code = """
        (define t (make-node 5 nil nil))
        (and (node? t) (= (node-value t) 5) (null? (node-left t)) (null? (node-right t)))
        """
        result = eval_source(code, env)
        assert result is True

    def test_complex_tree_structure(self, bst_env_and_output):
        """Test a more complex tree with many insertions."""
        env, demo_output = bst_env_and_output

        code = "(tree-inorder (tree-from-list (list 10 5 15 3 7 12 20 1 4 6 8 11 13 18 25)))"
        result = eval_source(code, env)
        assert result == PebbleList((1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 18, 20, 25))

    def test_tree_contains_multiple_values(self, bst_env_and_output):
        """Test tree-contains? with multiple checks on the same tree."""
        env, demo_output = bst_env_and_output

        code = """
        (define t (tree-from-list (list 5 3 8 1 4 7 9 2)))
        (list (tree-contains? t 1)
              (tree-contains? t 5)
              (tree-contains? t 9)
              (tree-contains? t 2)
              (tree-contains? t 0)
              (tree-contains? t 10))
        """
        result = eval_source(code, env)
        assert result == PebbleList((True, True, True, True, False, False))
