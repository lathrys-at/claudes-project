"""Tests for the Pebble CLI."""
import pytest
import tempfile
import os
import sys
from io import StringIO
from pebble.cli import main


class TestCLI:
    """Test the CLI main function."""

    def test_c_flag_simple_expr(self, capsys):
        """Test -c flag with simple expression."""
        main(["-c", "(+ 1 2)"])
        captured = capsys.readouterr()
        assert captured.out == "3\n"
        assert captured.err == ""

    def test_c_flag_with_sort(self, capsys):
        """Test -c flag with sort, confirming prelude is loaded."""
        main(["-c", "(sort (list 3 1 2))"])
        captured = capsys.readouterr()
        assert captured.out == "(1 2 3)\n"
        assert captured.err == ""

    def test_c_flag_multiple_forms(self, capsys):
        """Test -c flag with multiple forms, should print only last."""
        main(["-c", "(+ 1 2) (* 3 4)"])
        captured = capsys.readouterr()
        # Should print the result of the last form: (* 3 4) = 12
        assert captured.out == "12\n"
        assert captured.err == ""

    def test_c_flag_missing_expr(self, capsys):
        """Test -c flag without expression argument."""
        with pytest.raises(SystemExit) as exc_info:
            main(["-c"])
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "error:" in captured.err
        assert "-c requires an expression argument" in captured.err

    def test_c_flag_read_error(self, capsys):
        """Test -c flag with invalid Pebble syntax."""
        with pytest.raises(SystemExit) as exc_info:
            main(["-c", "(+ 1 2"])
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "error:" in captured.err

    def test_c_flag_eval_error(self, capsys):
        """Test -c flag with undefined symbol."""
        with pytest.raises(SystemExit) as exc_info:
            main(["-c", "(+ 1 undefined-symbol)"])
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "error:" in captured.err

    def test_file_mode_basic(self, capsys):
        """Test running a basic file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("(+ 5 7)\n")
            f.flush()
            temp_path = f.name

        try:
            main([temp_path])
            captured = capsys.readouterr()
            # File mode doesn't print output unless explicitly printed by the program
            assert captured.err == ""
        finally:
            os.unlink(temp_path)

    def test_file_mode_with_print(self, capsys):
        """Test running a file that prints output."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("(print (+ 5 7))\n")
            f.flush()
            temp_path = f.name

        try:
            main([temp_path])
            captured = capsys.readouterr()
            assert "12" in captured.out
        finally:
            os.unlink(temp_path)

    def test_file_mode_nonexistent_file(self, capsys):
        """Test running a nonexistent file."""
        with pytest.raises(SystemExit) as exc_info:
            main(["/nonexistent/file.pebble"])
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "error:" in captured.err
        assert "file not found" in captured.err

    def test_file_mode_read_error(self, capsys):
        """Test running a file with read error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("(+ 1 2\n")  # Missing closing paren
            f.flush()
            temp_path = f.name

        try:
            with pytest.raises(SystemExit) as exc_info:
                main([temp_path])
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "error:" in captured.err
        finally:
            os.unlink(temp_path)

    def test_file_mode_eval_error(self, capsys):
        """Test running a file with eval error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("(+ 1 undefined-var)\n")
            f.flush()
            temp_path = f.name

        try:
            with pytest.raises(SystemExit) as exc_info:
                main([temp_path])
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "error:" in captured.err
        finally:
            os.unlink(temp_path)

    def test_file_fizzbuzz(self, capsys):
        """Test running the fizzbuzz example."""
        fizzbuzz_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "fizzbuzz.pebble"
        )
        main([fizzbuzz_path])
        captured = capsys.readouterr()
        # Check for key fizzbuzz outputs
        assert "1\n" in captured.out or captured.out.startswith("1\n")
        assert "Fizz" in captured.out
        assert "Buzz" in captured.out
        assert "FizzBuzz" in captured.out

    def test_default_argv_uses_sys_argv(self, capsys, monkeypatch):
        """Test that main() without argv argument uses sys.argv."""
        original_argv = sys.argv
        try:
            monkeypatch.setattr(sys, "argv", ["pebble", "-c", "(+ 1 2)"])
            main()
            captured = capsys.readouterr()
            assert captured.out == "3\n"
        finally:
            sys.argv = original_argv

    def test_empty_file(self, capsys):
        """Test running an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("")
            f.flush()
            temp_path = f.name

        try:
            main([temp_path])
            captured = capsys.readouterr()
            # Empty file should not produce any output or errors
            assert captured.err == ""
        finally:
            os.unlink(temp_path)

    def test_c_flag_with_string_literal(self, capsys):
        """Test -c flag with string literal."""
        main(["-c", '(string-append "hello" " " "world")'])
        captured = capsys.readouterr()
        assert "hello world" in captured.out
        assert captured.err == ""

    def test_c_flag_with_boolean_true(self, capsys):
        """Test -c flag with boolean true."""
        main(["-c", "true"])
        captured = capsys.readouterr()
        assert "true" in captured.out
        assert captured.err == ""

    def test_c_flag_with_boolean_false(self, capsys):
        """Test -c flag with boolean false."""
        main(["-c", "false"])
        captured = capsys.readouterr()
        assert "false" in captured.out
        assert captured.err == ""
