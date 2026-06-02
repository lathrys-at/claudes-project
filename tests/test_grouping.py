"""Tests for frequencies and group-by hash-map utility functions."""

import pytest
from pebble.evaluator import make_global_env, seval
from pebble.reader import read_one


class TestFrequencies:
    """Test the frequencies function."""

    def test_frequencies_basic_numbers(self):
        """Test frequencies with numeric elements."""
        env = make_global_env()
        seval(read_one("(define result (frequencies (list 1 2 2 3 3 3)))"), env)
        # Verify using hash-ref and hash-count since key order is not guaranteed
        assert seval(read_one("(hash-ref result 1)"), env) == 1
        assert seval(read_one("(hash-ref result 2)"), env) == 2
        assert seval(read_one("(hash-ref result 3)"), env) == 3
        assert seval(read_one("(hash-count result)"), env) == 3

    def test_frequencies_symbols(self):
        """Test frequencies with symbol elements."""
        env = make_global_env()
        seval(
            read_one("(define result (frequencies (list (quote a) (quote b) (quote a) (quote c) (quote a))))"),
            env
        )
        assert seval(read_one("(hash-ref result (quote a))"), env) == 3
        assert seval(read_one("(hash-ref result (quote b))"), env) == 1
        assert seval(read_one("(hash-ref result (quote c))"), env) == 1
        assert seval(read_one("(hash-count result)"), env) == 3

    def test_frequencies_strings(self):
        """Test frequencies with string elements."""
        env = make_global_env()
        seval(
            read_one('(define result (frequencies (list "hello" "world" "hello")))'),
            env
        )
        assert seval(read_one('(hash-ref result "hello")'), env) == 2
        assert seval(read_one('(hash-ref result "world")'), env) == 1
        assert seval(read_one("(hash-count result)"), env) == 2

    def test_frequencies_empty_list(self):
        """Test frequencies with empty list."""
        env = make_global_env()
        seval(read_one("(define result (frequencies nil))"), env)
        assert seval(read_one("(hash-count result)"), env) == 0

    def test_frequencies_single_element(self):
        """Test frequencies with a single element list."""
        env = make_global_env()
        seval(read_one("(define result (frequencies (list 42)))"), env)
        assert seval(read_one("(hash-ref result 42)"), env) == 1
        assert seval(read_one("(hash-count result)"), env) == 1

    def test_frequencies_all_unique(self):
        """Test frequencies when all elements are unique."""
        env = make_global_env()
        seval(
            read_one("(define result (frequencies (list 1 2 3 4 5)))"),
            env
        )
        for i in range(1, 6):
            assert seval(read_one(f"(hash-ref result {i})"), env) == 1
        assert seval(read_one("(hash-count result)"), env) == 5

    def test_frequencies_all_same(self):
        """Test frequencies when all elements are the same."""
        env = make_global_env()
        seval(
            read_one("(define result (frequencies (list 5 5 5 5)))"),
            env
        )
        assert seval(read_one("(hash-ref result 5)"), env) == 4
        assert seval(read_one("(hash-count result)"), env) == 1


class TestGroupBy:
    """Test the group-by function."""

    def test_group_by_even_odd(self):
        """Test group-by with even? predicate."""
        env = make_global_env()
        seval(
            read_one("(define result (group-by even? (list 1 2 3 4 5 6)))"),
            env
        )
        # Verify lists have correct elements in original order
        assert seval(read_one("(= (hash-ref result true) (quote (2 4 6)))"), env)
        assert seval(read_one("(= (hash-ref result false) (quote (1 3 5)))"), env)
        assert seval(read_one("(hash-count result)"), env) == 2

    def test_group_by_string_length(self):
        """Test group-by with string-length."""
        env = make_global_env()
        seval(
            read_one('(define result (group-by (lambda (s) (string-length s)) (list "a" "bb" "cc" "d")))'),
            env
        )
        # Verify lists preserve order
        assert seval(read_one('(= (hash-ref result 1) (quote ("a" "d")))'), env)
        assert seval(read_one('(= (hash-ref result 2) (quote ("bb" "cc")))'), env)
        assert seval(read_one("(hash-count result)"), env) == 2

    def test_group_by_empty_list(self):
        """Test group-by with empty list."""
        env = make_global_env()
        seval(
            read_one("(define result (group-by even? nil))"),
            env
        )
        assert seval(read_one("(hash-count result)"), env) == 0

    def test_group_by_single_element(self):
        """Test group-by with single element."""
        env = make_global_env()
        seval(
            read_one("(define result (group-by even? (list 3)))"),
            env
        )
        assert seval(read_one("(= (hash-ref result false) (quote (3)))"), env)
        assert seval(read_one("(hash-count result)"), env) == 1

    def test_group_by_preserves_order_within_groups(self):
        """Test that group-by preserves original order within each group."""
        env = make_global_env()
        seval(
            read_one("(define result (group-by (lambda (x) (if (< x 3) (quote small) (quote large))) (list 1 5 2 6 3 4)))"),
            env
        )
        # Order should be preserved
        assert seval(read_one("(= (hash-ref result (quote small)) (quote (1 2)))"), env)
        assert seval(read_one("(= (hash-ref result (quote large)) (quote (5 6 3 4)))"), env)

    def test_group_by_all_same_key(self):
        """Test group-by when all elements map to the same key."""
        env = make_global_env()
        seval(
            read_one("(define result (group-by (lambda (x) (quote same)) (list 1 2 3)))"),
            env
        )
        assert seval(read_one("(= (hash-ref result (quote same)) (quote (1 2 3)))"), env)
        assert seval(read_one("(hash-count result)"), env) == 1

    def test_group_by_different_keys(self):
        """Test group-by when each element maps to a different key."""
        env = make_global_env()
        seval(
            read_one("(define result (group-by (lambda (x) x) (list 1 2 3)))"),
            env
        )
        assert seval(read_one("(= (hash-ref result 1) (quote (1)))"), env)
        assert seval(read_one("(= (hash-ref result 2) (quote (2)))"), env)
        assert seval(read_one("(= (hash-ref result 3) (quote (3)))"), env)
        assert seval(read_one("(hash-count result)"), env) == 3

    def test_group_by_with_symbols(self):
        """Test group-by grouping by odd/even using symbols as elements."""
        env = make_global_env()
        # Use symbols in a list and group by their length as strings
        seval(
            read_one("(define result (group-by (lambda (s) (string-length (symbol->string s))) (list (quote a) (quote bb) (quote c) (quote ddd))))"),
            env
        )
        # Group by string length: 1, 2, 3
        assert seval(read_one('(= (hash-ref result 1) (quote (a c)))'), env)
        assert seval(read_one('(= (hash-ref result 2) (quote (bb)))'), env)
        assert seval(read_one('(= (hash-ref result 3) (quote (ddd)))'), env)
