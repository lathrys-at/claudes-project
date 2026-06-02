"""Tests for JSON parser and serializer."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


def _load_json_example():
    """Load json.pebble and capture output, return env."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "json.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def json_env_and_output():
    """Load json.pebble once and capture its output."""
    return _load_json_example()


class TestJSONDemo:
    """Test the demo output when json.pebble is evaluated."""

    def test_demo_output(self, json_env_and_output):
        """Test that the demo code produces expected output."""
        env, demo_output = json_env_and_output
        lines = demo_output.strip().split('\n')
        assert len(lines) == 2
        assert lines[0] == '{"a": 1, "b": 2}'
        assert lines[1] == '[1, 2, 3]'


class TestJSONParsing:
    """Test the json-parse function."""

    def test_parse_integer(self, json_env_and_output):
        """Test parsing integers."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "42")', env)
        assert result == 42

    def test_parse_negative_integer(self, json_env_and_output):
        """Test parsing negative integers."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "-7")', env)
        assert result == -7

    def test_parse_true(self, json_env_and_output):
        """Test parsing true."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "true")', env)
        assert result is True

    def test_parse_false(self, json_env_and_output):
        """Test parsing false."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "false")', env)
        assert result is False

    def test_parse_string(self, json_env_and_output):
        """Test parsing strings."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "\\"hello\\"")', env)
        assert result == "hello"

    def test_parse_empty_array(self, json_env_and_output):
        """Test parsing empty array."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "[]")', env)
        assert result == PebbleList(())  # nil in Pebble is empty PebbleList

    def test_parse_array_with_elements(self, json_env_and_output):
        """Test parsing array with elements."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "[1, 2, 3]")', env)
        assert result == PebbleList((1, 2, 3))

    def test_parse_empty_object(self, json_env_and_output):
        """Test parsing empty object."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "{}")', env)
        # Result is a hash map - check it directly
        is_hash = eval_source('(hash? (json-parse "{}"))', env)
        assert is_hash

    def test_parse_object_with_entries(self, json_env_and_output):
        """Test parsing object with entries."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "{\\"a\\": 1, \\"b\\": 2}")', env)
        # Check that we got a hash map
        is_hash = eval_source('(hash? (json-parse "{\\"a\\": 1, \\"b\\": 2}"))', env)
        assert is_hash
        # Check values
        a_val = eval_source('(hash-ref (json-parse "{\\"a\\": 1, \\"b\\": 2}") "a")', env)
        b_val = eval_source('(hash-ref (json-parse "{\\"a\\": 1, \\"b\\": 2}") "b")', env)
        assert a_val == 1
        assert b_val == 2

    def test_parse_nested_structure(self, json_env_and_output):
        """Test parsing nested object with array."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "{\\"nums\\": [1, 2, 3], \\"ok\\": true}")', env)
        is_hash = eval_source('(hash? (json-parse "{\\"nums\\": [1, 2, 3], \\"ok\\": true}"))', env)
        assert is_hash
        nums_val = eval_source('(hash-ref (json-parse "{\\"nums\\": [1, 2, 3], \\"ok\\": true}") "nums")', env)
        ok_val = eval_source('(hash-ref (json-parse "{\\"nums\\": [1, 2, 3], \\"ok\\": true}") "ok")', env)
        assert nums_val == PebbleList((1, 2, 3))
        assert ok_val is True

    def test_parse_whitespace_tolerance(self, json_env_and_output):
        """Test that parser tolerates whitespace."""
        env, _ = json_env_and_output
        result = eval_source('(json-parse "  [ 1 , 2 ]  ")', env)
        assert result == PebbleList((1, 2))

    def test_parse_string_with_escape(self, json_env_and_output):
        """Test parsing string with escape sequence."""
        env, _ = json_env_and_output
        # Build the JSON string: "a\nb" (with literal backslash-n)
        # We do this by concatenating: " + a + \ + n + b + "
        eval_source('(define escape_test_str (string-append "\\"" "a" "\\\\" "n" "b" "\\""))', env)
        result = eval_source('(json-parse escape_test_str)', env)
        # JSON parsing of \n produces a newline, so result should be: a, newline, b
        assert result == "a\nb"
        assert len(result) == 3


class TestJSONSerialization:
    """Test the json-serialize function."""

    def test_serialize_integer(self, json_env_and_output):
        """Test serializing integers."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize 42)', env)
        assert result == "42"

    def test_serialize_negative_integer(self, json_env_and_output):
        """Test serializing negative integers."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize -7)', env)
        assert result == "-7"

    def test_serialize_true(self, json_env_and_output):
        """Test serializing true."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize true)', env)
        assert result == "true"

    def test_serialize_false(self, json_env_and_output):
        """Test serializing false."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize false)', env)
        assert result == "false"

    def test_serialize_string(self, json_env_and_output):
        """Test serializing strings."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize "hi")', env)
        # Should be the 4-character string: "hi"
        assert result == '"hi"'
        assert len(result) == 4

    def test_serialize_empty_array(self, json_env_and_output):
        """Test serializing empty array."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize nil)', env)
        assert result == "[]"

    def test_serialize_array(self, json_env_and_output):
        """Test serializing array."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (list 1 2 3))', env)
        assert result == "[1, 2, 3]"

    def test_serialize_empty_object(self, json_env_and_output):
        """Test serializing empty object."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (make-hash))', env)
        assert result == "{}"

    def test_serialize_object(self, json_env_and_output):
        """Test serializing object."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (make-hash "a" 1 "b" 2))', env)
        assert result == '{"a": 1, "b": 2}'


class TestJSONRoundTrip:
    """Test round-trip parsing and serialization."""

    def test_roundtrip_integer(self, json_env_and_output):
        """Test round-trip for integer."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (json-parse "42"))', env)
        assert result == "42"

    def test_roundtrip_array(self, json_env_and_output):
        """Test round-trip for array."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (json-parse "[1, 2, 3]"))', env)
        assert result == "[1, 2, 3]"

    def test_roundtrip_empty_object(self, json_env_and_output):
        """Test round-trip for empty object."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (json-parse "{}"))', env)
        assert result == "{}"

    def test_roundtrip_simple_object(self, json_env_and_output):
        """Test round-trip for simple object."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (json-parse "{\\"a\\": 1, \\"b\\": 2}"))', env)
        assert result == '{"a": 1, "b": 2}'

    def test_roundtrip_nested_object(self, json_env_and_output):
        """Test round-trip for nested object with array."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (json-parse "{\\"nums\\": [1, 2, 3], \\"ok\\": true}"))', env)
        assert result == '{"nums": [1, 2, 3], "ok": true}'

    def test_roundtrip_empty_array(self, json_env_and_output):
        """Test round-trip for empty array."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (json-parse "[]"))', env)
        assert result == "[]"

    def test_roundtrip_boolean_true(self, json_env_and_output):
        """Test round-trip for boolean true."""
        env, _ = json_env_and_output
        result = eval_source('(json-serialize (json-parse "true"))', env)
        assert result == "true"
