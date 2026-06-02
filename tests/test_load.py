"""Tests for the load special form."""
import pytest
from pebble.evaluator import seval, make_global_env, EvalError
from pebble.types import Symbol, PebbleList, NIL
from pebble.reader import read_one


class TestLoadBasics:
    """Test basic load functionality."""

    def test_load_definition(self, tmp_path):
        """Test loading a file with a simple definition."""
        # Create a temp file with a definition
        test_file = tmp_path / "test.pebble"
        test_file.write_text("(define loaded-value 42)")

        env = make_global_env()
        # Load the file
        result = seval(read_one(f'(load "{test_file}")'), env)

        # Check that the definition is now in the environment
        assert seval(Symbol("loaded-value"), env) == 42

    def test_load_function_definition(self, tmp_path):
        """Test loading a file with a function definition."""
        # Create a temp file with a function
        test_file = tmp_path / "test.pebble"
        test_file.write_text("(define (square x) (* x x))")

        env = make_global_env()
        # Load the file
        seval(read_one(f'(load "{test_file}")'), env)

        # Check that we can call the function
        result = seval(read_one("(square 5)"), env)
        assert result == 25

    def test_load_returns_last_form(self, tmp_path):
        """Test that load returns the value of the last form."""
        test_file = tmp_path / "test.pebble"
        test_file.write_text("(define x 10)\n(+ x 5)")

        env = make_global_env()
        result = seval(read_one(f'(load "{test_file}")'), env)

        # The last form (+ x 5) should return 15
        assert result == 15

    def test_load_empty_file(self, tmp_path):
        """Test loading an empty file returns nil."""
        test_file = tmp_path / "empty.pebble"
        test_file.write_text("")

        env = make_global_env()
        result = seval(read_one(f'(load "{test_file}")'), env)

        # Should return NIL
        assert result == NIL

    def test_load_file_with_only_comments(self, tmp_path):
        """Test loading a file with only comments returns nil."""
        test_file = tmp_path / "comments.pebble"
        test_file.write_text("; This is a comment\n; Another comment")

        env = make_global_env()
        result = seval(read_one(f'(load "{test_file}")'), env)

        # Should return NIL
        assert result == NIL

    def test_load_macro_definition(self, tmp_path):
        """Test loading a file with a macro definition."""
        test_file = tmp_path / "macro.pebble"
        test_file.write_text("""(define-macro (triple x)
  `(* 3 ,x))""")

        env = make_global_env()
        seval(read_one(f'(load "{test_file}")'), env)

        # Check that we can use the macro
        result = seval(read_one("(triple 7)"), env)
        assert result == 21

    def test_load_nonexistent_file(self, tmp_path):
        """Test that loading a nonexistent file raises EvalError."""
        nonexistent = tmp_path / "nonexistent.pebble"

        env = make_global_env()
        with pytest.raises(EvalError) as exc_info:
            seval(read_one(f'(load "{nonexistent}")'), env)

        # The error message should mention the file
        assert "nonexistent.pebble" in str(exc_info.value)

    def test_load_parse_error(self, tmp_path):
        """Test that a file with parse errors raises EvalError."""
        test_file = tmp_path / "bad.pebble"
        test_file.write_text("(define x 10")

        env = make_global_env()
        with pytest.raises(EvalError) as exc_info:
            seval(read_one(f'(load "{test_file}")'), env)

        # The error message should be about parsing
        assert "parse error" in str(exc_info.value).lower()

    def test_load_with_wrong_args(self):
        """Test that load with wrong number of arguments raises EvalError."""
        env = make_global_env()

        # Load with no arguments
        with pytest.raises(EvalError) as exc_info:
            seval(read_one("(load)"), env)
        assert "exactly 1 argument" in str(exc_info.value)

        # Load with too many arguments
        with pytest.raises(EvalError) as exc_info:
            seval(read_one('(load "file1" "file2")'), env)
        assert "exactly 1 argument" in str(exc_info.value)

    def test_load_non_string_path(self, tmp_path):
        """Test that load with non-string path raises EvalError."""
        env = make_global_env()

        with pytest.raises(EvalError) as exc_info:
            seval(read_one("(load 42)"), env)
        assert "string" in str(exc_info.value).lower()

    def test_load_eval_error_propagates(self, tmp_path):
        """Test that evaluation errors in loaded forms propagate."""
        test_file = tmp_path / "error.pebble"
        # This file will have an evaluation error (undefined symbol)
        test_file.write_text("(undefined-symbol)")

        env = make_global_env()
        with pytest.raises(EvalError):
            seval(read_one(f'(load "{test_file}")'), env)

    def test_transitive_load(self, tmp_path):
        """Test that a loaded file can load another file."""
        # Create the second file (loaded by the first)
        file2 = tmp_path / "file2.pebble"
        file2.write_text("(define inner-value 99)")

        # Create the first file (which loads the second)
        file1 = tmp_path / "file1.pebble"
        file1.write_text(f'(load "{file2}")\n(define outer-value 88)')

        env = make_global_env()
        seval(read_one(f'(load "{file1}")'), env)

        # Both definitions should be visible
        assert seval(Symbol("outer-value"), env) == 88
        assert seval(Symbol("inner-value"), env) == 99

    def test_load_multiple_forms(self, tmp_path):
        """Test loading a file with multiple forms."""
        test_file = tmp_path / "multi.pebble"
        test_file.write_text("""
(define x 10)
(define y 20)
(define (add-xy) (+ x y))
(add-xy)
""")

        env = make_global_env()
        result = seval(read_one(f'(load "{test_file}")'), env)

        # The result should be the last form's value
        assert result == 30
        # All definitions should be available
        assert seval(Symbol("x"), env) == 10
        assert seval(Symbol("y"), env) == 20
