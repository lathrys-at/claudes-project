"""Tests for the Pebble printer."""
import pytest
from pebble.types import Symbol, PebbleList, NIL
from pebble.evaluator import Procedure, Environment, make_global_env
from pebble.reader import read_one
from pebble.printer import pebble_repr, pebble_str


class TestPebbleRepr:
    """Test pebble_repr function."""

    def test_true(self):
        """True should repr as 'true'."""
        assert pebble_repr(True) == "true"

    def test_false(self):
        """False should repr as 'false'."""
        assert pebble_repr(False) == "false"

    def test_nil(self):
        """Empty PebbleList should repr as 'nil'."""
        assert pebble_repr(NIL) == "nil"

    def test_integer(self):
        """Integers should repr as their string form."""
        assert pebble_repr(42) == "42"
        assert pebble_repr(-5) == "-5"
        assert pebble_repr(0) == "0"

    def test_float(self):
        """Floats should repr as their string form."""
        assert pebble_repr(3.14) == "3.14"
        assert pebble_repr(-2.5) == "-2.5"

    def test_symbol(self):
        """Symbols should repr as their text."""
        assert pebble_repr(Symbol("foo")) == "foo"
        assert pebble_repr(Symbol("+")) == "+"

    def test_string_no_escapes(self):
        """Strings without special chars should have quotes."""
        assert pebble_repr("hello") == '"hello"'

    def test_string_with_escapes(self):
        """Strings with special chars should be escaped in repr."""
        assert pebble_repr('hello"world') == '"hello\\"world"'
        assert pebble_repr("hello\nworld") == '"hello\\nworld"'
        assert pebble_repr("hello\\world") == '"hello\\\\world"'

    def test_simple_list(self):
        """Simple lists should repr with parens and spaces."""
        lst = PebbleList([Symbol("a"), Symbol("b"), Symbol("c")])
        assert pebble_repr(lst) == "(a b c)"

    def test_nested_list(self):
        """Nested lists should repr recursively."""
        lst = PebbleList([Symbol("a"), PebbleList([Symbol("b"), 2]), "hi"])
        assert pebble_repr(lst) == '(a (b 2) "hi")'

    def test_list_with_numbers_and_symbols(self):
        """Lists with mixed content should repr correctly."""
        lst = PebbleList([Symbol("define"), Symbol("x"), 42])
        assert pebble_repr(lst) == "(define x 42)"

    def test_procedure(self):
        """Procedures should use their repr()."""
        env = Environment()
        proc = Procedure([Symbol("x"), Symbol("y")], [], env)
        result = pebble_repr(proc)
        assert result == repr(proc)
        assert "<procedure" in result

    def test_builtin(self):
        """Builtin functions should repr as '<builtin>'."""
        def dummy_func():
            pass
        assert pebble_repr(dummy_func) == "<builtin>"

    def test_round_trip_symbol(self):
        """read_one(pebble_repr(x)) should reconstruct x for symbols."""
        sym = Symbol("hello")
        assert read_one(pebble_repr(sym)) == sym

    def test_round_trip_list(self):
        """read_one(pebble_repr(x)) should reconstruct x for lists."""
        lst = PebbleList([Symbol("a"), PebbleList([Symbol("b"), 2])])
        reconstructed = read_one(pebble_repr(lst))
        assert reconstructed == lst

    def test_round_trip_string(self):
        """read_one(pebble_repr(x)) should reconstruct x for strings."""
        s = "hello\nworld"
        reconstructed = read_one(pebble_repr(s))
        assert reconstructed == s


class TestPebbleStr:
    """Test pebble_str function."""

    def test_true(self):
        """True should str as 'true'."""
        assert pebble_str(True) == "true"

    def test_false(self):
        """False should str as 'false'."""
        assert pebble_str(False) == "false"

    def test_nil(self):
        """Empty PebbleList should str as 'nil'."""
        assert pebble_str(NIL) == "nil"

    def test_integer(self):
        """Integers should str as their string form."""
        assert pebble_str(42) == "42"

    def test_float(self):
        """Floats should str as their string form."""
        assert pebble_str(3.14) == "3.14"

    def test_symbol(self):
        """Symbols should str as their text."""
        assert pebble_str(Symbol("foo")) == "foo"

    def test_string_raw(self):
        """Strings should str as their raw text (no quotes, no escaping)."""
        assert pebble_str("hello") == "hello"
        assert pebble_str('hello"world') == 'hello"world'
        assert pebble_str("hello\nworld") == "hello\nworld"

    def test_list(self):
        """Lists should str like repr (using pebble_repr internally for items)."""
        lst = PebbleList([Symbol("a"), 42, "test"])
        # Note: strings in the list should still be quoted in the list repr
        assert pebble_str(lst) == '(a 42 "test")'

    def test_procedure(self):
        """Procedures should str like repr."""
        env = Environment()
        proc = Procedure([Symbol("x")], [], env)
        assert pebble_str(proc) == repr(proc)

    def test_builtin(self):
        """Builtin functions should str as '<builtin>'."""
        def dummy_func():
            pass
        assert pebble_str(dummy_func) == "<builtin>"
