"""Tests for hash map data type and builtins."""
import pytest
from pebble.evaluator import make_global_env, EvalError, eval_source
from pebble.types import PebbleHash, PebbleList, Symbol, NIL
from pebble.printer import pebble_repr


def make_env():
    """Create a fresh global environment for each test."""
    return make_global_env()


def eval_in_env(source, env=None):
    """Evaluate source string in given environment and return result."""
    if env is None:
        env = make_env()
    return eval_source(source, env)


# ===== make-hash tests =====

def test_make_hash_empty():
    """Empty hash map created with make-hash."""
    env = make_env()
    result = eval_in_env("(make-hash)")
    assert isinstance(result, PebbleHash)
    assert len(result) == 0


def test_make_hash_from_pairs():
    """Hash map created from key-value pairs."""
    env = make_env()
    result = eval_in_env('(make-hash "a" 1 "b" 2)')
    assert isinstance(result, PebbleHash)
    assert len(result) == 2
    assert result.get("a") == 1
    assert result.get("b") == 2


def test_make_hash_odd_args_raises():
    """Odd number of arguments to make-hash raises EvalError."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(make-hash "a" 1 "b")')


def test_make_hash_single_pair():
    """Hash map with single pair."""
    env = make_env()
    result = eval_in_env('(make-hash 1 "one")')
    assert isinstance(result, PebbleHash)
    assert len(result) == 1
    assert result.get(1) == "one"


# ===== hash? tests =====

def test_hash_p_true_for_hash():
    """hash? returns true for hash maps."""
    env = make_env()
    assert eval_in_env('(hash? (make-hash))') is True
    assert eval_in_env('(hash? (make-hash "a" 1))') is True


def test_hash_p_false_for_non_hash():
    """hash? returns false for non-hash values."""
    env = make_env()
    assert eval_in_env('(hash? 42)') is False
    assert eval_in_env('(hash? "string")') is False
    assert eval_in_env('(hash? (list 1 2))') is False
    assert eval_in_env('(hash? nil)') is False


# ===== hash-set tests =====

def test_hash_set_add_to_empty():
    """hash-set adds a key-value pair to empty map."""
    env = make_env()
    result = eval_in_env('(hash-set (make-hash) "x" 42)')
    assert isinstance(result, PebbleHash)
    assert len(result) == 1
    assert result.get("x") == 42


def test_hash_set_add_to_existing():
    """hash-set adds a new pair to non-empty map."""
    env = make_env()
    result = eval_in_env('(hash-set (make-hash "a" 1) "b" 2)')
    assert len(result) == 2
    assert result.get("a") == 1
    assert result.get("b") == 2


def test_hash_set_replace():
    """hash-set replaces existing key."""
    env = make_env()
    result = eval_in_env('(hash-set (make-hash "a" 1) "a" 2)')
    assert len(result) == 1
    assert result.get("a") == 2


def test_hash_set_immutability():
    """hash-set does not modify original map."""
    env = make_env()
    eval_in_env('(define m (make-hash "a" 1))', env)
    eval_in_env('(define m2 (hash-set m "b" 2))', env)

    m = env.lookup("m")
    m2 = env.lookup("m2")

    assert len(m) == 1
    assert "a" in m
    assert "b" not in m

    assert len(m2) == 2
    assert "a" in m2
    assert "b" in m2


def test_hash_set_non_hash_raises():
    """hash-set raises EvalError if first arg is not a hash."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-set (list 1 2) "k" 1)')


# ===== hash-ref tests =====

def test_hash_ref_existing_key():
    """hash-ref returns value for existing key."""
    env = make_env()
    result = eval_in_env('(hash-ref (make-hash "a" 42) "a")')
    assert result == 42


def test_hash_ref_missing_key_raises():
    """hash-ref raises EvalError for missing key (no default)."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-ref (make-hash) "missing")')


def test_hash_ref_missing_key_with_default():
    """hash-ref returns default for missing key."""
    env = make_env()
    result = eval_in_env('(hash-ref (make-hash) "missing" "default")')
    assert result == "default"


def test_hash_ref_existing_key_with_default():
    """hash-ref returns value (not default) when key exists."""
    env = make_env()
    result = eval_in_env('(hash-ref (make-hash "a" 42) "a" 99)')
    assert result == 42


def test_hash_ref_non_hash_raises():
    """hash-ref raises EvalError if first arg is not a hash."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-ref (list 1 2) "k")')


# ===== hash-has? tests =====

def test_hash_has_p_true():
    """hash-has? returns true for existing key."""
    env = make_env()
    assert eval_in_env('(hash-has? (make-hash "a" 1) "a")') is True


def test_hash_has_p_false():
    """hash-has? returns false for missing key."""
    env = make_env()
    assert eval_in_env('(hash-has? (make-hash "a" 1) "b")') is False


def test_hash_has_p_empty_map():
    """hash-has? returns false for empty map."""
    env = make_env()
    assert eval_in_env('(hash-has? (make-hash) "x")') is False


# ===== hash-remove tests =====

def test_hash_remove_existing_key():
    """hash-remove removes existing key."""
    env = make_env()
    result = eval_in_env('(hash-remove (make-hash "a" 1 "b" 2) "a")')
    assert len(result) == 1
    assert "a" not in result
    assert result.get("b") == 2


def test_hash_remove_missing_key():
    """hash-remove is no-op for missing key."""
    env = make_env()
    result = eval_in_env('(hash-remove (make-hash "a" 1) "missing")')
    assert len(result) == 1
    assert result.get("a") == 1


def test_hash_remove_immutability():
    """hash-remove does not modify original map."""
    env = make_env()
    eval_in_env('(define m (make-hash "a" 1 "b" 2))', env)
    eval_in_env('(define m2 (hash-remove m "a"))', env)

    m = env.lookup("m")
    m2 = env.lookup("m2")

    assert len(m) == 2
    assert "a" in m

    assert len(m2) == 1
    assert "a" not in m2
    assert "b" in m2


# ===== hash-count tests =====

def test_hash_count_empty():
    """hash-count returns 0 for empty map."""
    env = make_env()
    assert eval_in_env('(hash-count (make-hash))') == 0


def test_hash_count_nonempty():
    """hash-count returns count for non-empty map."""
    env = make_env()
    assert eval_in_env('(hash-count (make-hash "a" 1))') == 1
    assert eval_in_env('(hash-count (make-hash "a" 1 "b" 2 "c" 3))') == 3


# ===== hash-keys tests =====

def test_hash_keys_empty():
    """hash-keys returns empty list for empty map."""
    env = make_env()
    result = eval_in_env('(hash-keys (make-hash))')
    assert isinstance(result, PebbleList)
    assert len(result) == 0


def test_hash_keys_nonempty():
    """hash-keys returns list of keys."""
    env = make_env()
    m = eval_in_env('(make-hash "a" 1 "b" 2)')
    result = eval_in_env('(hash-keys (make-hash "a" 1 "b" 2))')

    assert isinstance(result, PebbleList)
    assert len(result) == 2
    assert "a" in result
    assert "b" in result


# ===== hash-values tests =====

def test_hash_values_empty():
    """hash-values returns empty list for empty map."""
    env = make_env()
    result = eval_in_env('(hash-values (make-hash))')
    assert isinstance(result, PebbleList)
    assert len(result) == 0


def test_hash_values_nonempty():
    """hash-values returns list of values."""
    env = make_env()
    result = eval_in_env('(hash-values (make-hash "a" 1 "b" 2))')

    assert isinstance(result, PebbleList)
    assert len(result) == 2
    assert 1 in result
    assert 2 in result


# ===== hash->list tests =====

def test_hash_to_list_empty():
    """hash->list returns empty list for empty map."""
    env = make_env()
    result = eval_in_env('(hash->list (make-hash))')
    assert isinstance(result, PebbleList)
    assert len(result) == 0


def test_hash_to_list_nonempty():
    """hash->list returns list of [key value] pairs."""
    env = make_env()
    result = eval_in_env('(hash->list (make-hash "a" 1 "b" 2))')

    assert isinstance(result, PebbleList)
    assert len(result) == 2

    # Each element should be a 2-element list
    for pair in result:
        assert isinstance(pair, PebbleList)
        assert len(pair) == 2

    # Check pairs can be found
    keys_found = [pair[0] for pair in result]
    assert "a" in keys_found
    assert "b" in keys_found


# ===== Equality tests =====

def test_hash_equality_same_pairs():
    """Two maps with same pairs are equal."""
    env = make_env()
    m1 = eval_in_env('(make-hash "a" 1 "b" 2)')
    m2 = eval_in_env('(make-hash "b" 2 "a" 1)')

    assert m1 == m2


def test_hash_equality_via_builtin():
    """Equality builtin works on hash maps."""
    env = make_env()
    assert eval_in_env('(= (make-hash "a" 1) (make-hash "a" 1))') is True
    assert eval_in_env('(= (make-hash "a" 1) (make-hash "a" 2))') is False


def test_hash_inequality_different_pairs():
    """Two maps with different pairs are not equal."""
    env = make_env()
    m1 = eval_in_env('(make-hash "a" 1)')
    m2 = eval_in_env('(make-hash "b" 2)')

    assert m1 != m2


def test_hash_inequality_different_sizes():
    """Maps with different sizes are not equal."""
    env = make_env()
    m1 = eval_in_env('(make-hash "a" 1)')
    m2 = eval_in_env('(make-hash "a" 1 "b" 2)')

    assert m1 != m2


# ===== Key type tests =====

def test_hash_integer_keys():
    """Integer keys work."""
    env = make_env()
    result = eval_in_env('(make-hash 1 "one" 2 "two")')
    assert result.get(1) == "one"
    assert result.get(2) == "two"


def test_hash_string_keys():
    """String keys work."""
    env = make_env()
    result = eval_in_env('(make-hash "a" 1 "b" 2)')
    assert result.get("a") == 1
    assert result.get("b") == 2


def test_hash_symbol_keys():
    """Symbol keys work."""
    env = make_env()
    result = eval_in_env("(make-hash 'x 10 'y 20)")
    assert result.get(Symbol("x")) == 10
    assert result.get(Symbol("y")) == 20


def test_hash_boolean_keys():
    """Boolean keys work."""
    env = make_env()
    result = eval_in_env('(make-hash true 1 false 0)')
    assert result.get(True) == 1
    assert result.get(False) == 0


def test_hash_float_keys():
    """Float keys work."""
    env = make_env()
    result = eval_in_env('(make-hash 1.5 "one-point-five" 2.5 "two-point-five")')
    assert result.get(1.5) == "one-point-five"
    assert result.get(2.5) == "two-point-five"


def test_hash_list_keys():
    """Empty list (nil) can be a key."""
    env = make_env()
    result = eval_in_env('(make-hash nil "empty")')
    assert result.get(NIL) == "empty"


# ===== Non-hash builtin error tests =====

def test_hash_set_on_list_raises():
    """hash-set on list raises EvalError."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-set (list 1 2) "k" 1)')


def test_hash_ref_on_list_raises():
    """hash-ref on list raises EvalError."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-ref (list 1 2) "k")')


def test_hash_has_on_list_raises():
    """hash-has? on list raises EvalError."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-has? (list 1 2) "k")')


def test_hash_remove_on_list_raises():
    """hash-remove on list raises EvalError."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-remove (list 1 2) "k")')


def test_hash_count_on_list_raises():
    """hash-count on list raises EvalError."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-count (list 1 2))')


def test_hash_keys_on_list_raises():
    """hash-keys on list raises EvalError."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-keys (list 1 2))')


def test_hash_values_on_list_raises():
    """hash-values on list raises EvalError."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash-values (list 1 2))')


def test_hash_to_list_on_list_raises():
    """hash->list on list raises EvalError."""
    env = make_env()
    with pytest.raises(EvalError):
        eval_in_env('(hash->list (list 1 2))')


# ===== Printer tests =====

def test_empty_hash_printer():
    """Empty hash map prints as {}."""
    h = PebbleHash()
    assert pebble_repr(h) == "{}"


def test_nonempty_hash_printer():
    """Non-empty hash map is printed in readable form."""
    h = PebbleHash({"a": 1})
    printed = pebble_repr(h)
    assert "a" in printed
    assert "1" in printed
    assert printed.startswith("{")
    assert printed.endswith("}")


def test_hash_printer_multiple_pairs():
    """Hash map with multiple pairs is printed correctly."""
    h = PebbleHash({"x": 10, "y": 20})
    printed = pebble_repr(h)
    assert "x" in printed
    assert "10" in printed
    assert "y" in printed
    assert "20" in printed
