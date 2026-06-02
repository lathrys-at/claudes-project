"""Tests for run-length encoding/decoding functions."""

import pytest
from pebble.evaluator import make_global_env, eval_source


def test_rle_encode_basic():
    """Test basic RLE encoding."""
    env = make_global_env()

    # (rle-encode (list 1 1 1 2 3 3))
    result = eval_source("(rle-encode (list 1 1 1 2 3 3))", env)
    expected = eval_source("(list (list 1 3) (list 2 1) (list 3 2))", env)
    assert result == expected, f"Expected {expected}, got {result}"


def test_rle_encode_empty():
    """Test RLE encoding of empty list."""
    env = make_global_env()

    # (rle-encode nil)
    result = eval_source("(rle-encode nil)", env)
    expected = eval_source("nil", env)
    assert result == expected, f"Expected {expected}, got {result}"


def test_rle_encode_single_element():
    """Test RLE encoding of single element."""
    env = make_global_env()

    # (rle-encode (list 5))
    result = eval_source("(rle-encode (list 5))", env)
    expected = eval_source("(list (list 5 1))", env)
    assert result == expected, f"Expected {expected}, got {result}"


def test_rle_encode_all_distinct():
    """Test RLE encoding of all distinct elements."""
    env = make_global_env()

    # (rle-encode (list 1 2 3))
    result = eval_source("(rle-encode (list 1 2 3))", env)
    expected = eval_source("(list (list 1 1) (list 2 1) (list 3 1))", env)
    assert result == expected, f"Expected {expected}, got {result}"


def test_rle_encode_single_run():
    """Test RLE encoding of single run."""
    env = make_global_env()

    # (rle-encode (list 4 4 4 4))
    result = eval_source("(rle-encode (list 4 4 4 4))", env)
    expected = eval_source("(list (list 4 4))", env)
    assert result == expected, f"Expected {expected}, got {result}"


def test_rle_encode_strings():
    """Test RLE encoding with strings."""
    env = make_global_env()

    # (rle-encode (list "a" "a" "b"))
    result = eval_source('(rle-encode (list "a" "a" "b"))', env)
    expected = eval_source('(list (list "a" 2) (list "b" 1))', env)
    assert result == expected, f"Expected {expected}, got {result}"


def test_rle_decode_basic():
    """Test basic RLE decoding."""
    env = make_global_env()

    # (rle-decode (list (list 1 3) (list 2 1) (list 3 2)))
    result = eval_source(
        "(rle-decode (list (list 1 3) (list 2 1) (list 3 2)))",
        env
    )
    expected = eval_source("(list 1 1 1 2 3 3)", env)
    assert result == expected, f"Expected {expected}, got {result}"


def test_rle_decode_empty():
    """Test RLE decoding of empty list."""
    env = make_global_env()

    # (rle-decode nil)
    result = eval_source("(rle-decode nil)", env)
    expected = eval_source("nil", env)
    assert result == expected, f"Expected {expected}, got {result}"


def test_rle_decode_single_run():
    """Test RLE decoding of single run."""
    env = make_global_env()

    # (rle-decode (list (list 4 4)))
    result = eval_source("(rle-decode (list (list 4 4)))", env)
    expected = eval_source("(list 4 4 4 4)", env)
    assert result == expected, f"Expected {expected}, got {result}"


def test_rle_round_trip_basic():
    """Test round-trip encoding and decoding."""
    env = make_global_env()

    original = "(list 1 1 1 2 3 3)"
    result = eval_source(
        f"(rle-decode (rle-encode {original}))",
        env
    )
    expected = eval_source(original, env)
    assert result == expected, f"Round-trip failed: {original}"


def test_rle_round_trip_single():
    """Test round-trip with single element."""
    env = make_global_env()

    original = "(list 5)"
    result = eval_source(
        f"(rle-decode (rle-encode {original}))",
        env
    )
    expected = eval_source(original, env)
    assert result == expected, f"Round-trip failed: {original}"


def test_rle_round_trip_distinct():
    """Test round-trip with all distinct elements."""
    env = make_global_env()

    original = "(list 1 2 3)"
    result = eval_source(
        f"(rle-decode (rle-encode {original}))",
        env
    )
    expected = eval_source(original, env)
    assert result == expected, f"Round-trip failed: {original}"


def test_rle_round_trip_long_run():
    """Test round-trip with long run."""
    env = make_global_env()

    original = "(list 7 7 7 7 7)"
    result = eval_source(
        f"(rle-decode (rle-encode {original}))",
        env
    )
    expected = eval_source(original, env)
    assert result == expected, f"Round-trip failed: {original}"


def test_rle_round_trip_symbols():
    """Test round-trip with symbols."""
    env = make_global_env()

    original = "(list 'a 'a 'b 'b 'b 'c)"
    result = eval_source(
        f"(rle-decode (rle-encode {original}))",
        env
    )
    expected = eval_source(original, env)
    assert result == expected, f"Round-trip failed: {original}"
