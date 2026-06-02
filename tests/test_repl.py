"""Tests for the Pebble REPL and file runner."""
import pytest
import tempfile
import os
from pebble.repl import repl, run_file
from pebble.evaluator import make_global_env, Environment


class InputCollector:
    """Helper to feed lines to the REPL and collect output."""

    def __init__(self, lines):
        """Initialize with a list of input lines.

        Args:
            lines: List of input strings (without newlines).
        """
        self.lines = iter(lines)
        self.outputs = []

    def input_fn(self, prompt=""):
        """Input function that feeds lines and raises EOFError when done."""
        try:
            return next(self.lines)
        except StopIteration:
            raise EOFError()

    def output_fn(self, text=""):
        """Output function that collects all output."""
        self.outputs.append(text)

    def get_outputs(self):
        """Get all collected outputs."""
        return self.outputs


class TestREPL:
    """Test the REPL."""

    def test_simple_evaluation(self):
        """Test evaluating a simple expression (+ 1 2)."""
        collector = InputCollector(["(+ 1 2)"])
        repl(input_fn=collector.input_fn, output_fn=collector.output_fn)
        outputs = collector.get_outputs()
        # Should have banner, result, blank line, and "Goodbye!"
        assert "Pebble Lisp REPL" in outputs[0]
        assert "3" in outputs[1]
        assert "Goodbye!" in outputs[-1]

    def test_multiline_input(self):
        """Test evaluating a multi-line form."""
        collector = InputCollector(["(+ 1", "2)"])
        repl(input_fn=collector.input_fn, output_fn=collector.output_fn)
        outputs = collector.get_outputs()
        # Should evaluate to 3
        assert "3" in outputs

    def test_define_and_use(self):
        """Test defining a variable and using it across prompts."""
        collector = InputCollector(["(define x 42)", "x"])
        repl(input_fn=collector.input_fn, output_fn=collector.output_fn)
        outputs = collector.get_outputs()
        # define returns the symbol name, then x evaluates to 42
        assert "x" in outputs  # define returns symbol x
        assert "42" in outputs  # x evaluates to 42

    def test_eval_error(self):
        """Test that eval errors are caught and printed."""
        collector = InputCollector(["(+ 1 undefined-symbol)"])
        repl(input_fn=collector.input_fn, output_fn=collector.output_fn)
        outputs = collector.get_outputs()
        # Should have error message
        found_error = any("error:" in output for output in outputs)
        assert found_error

    def test_eval_error_continues_repl(self):
        """Test that the REPL continues after an evaluation error.

        This is the key test for the control-flow fix: feed an error-producing
        input, then a valid input, and verify both are processed.
        """
        collector = InputCollector(["(+ 1 foo)", "(+ 10 20)"])
        repl(input_fn=collector.input_fn, output_fn=collector.output_fn)
        outputs = collector.get_outputs()

        # Check for the error message from the first line
        error_found = any("error:" in output for output in outputs)
        assert error_found, f"Expected error message in outputs: {outputs}"

        # Check for the successful result from the second line
        result_found = "30" in outputs
        assert result_found, f"Expected '30' in outputs after error: {outputs}"

    def test_read_error(self):
        """Test that read errors are caught and printed."""
        collector = InputCollector(["(+ 1 2"])  # Missing closing paren
        repl(input_fn=collector.input_fn, output_fn=collector.output_fn)
        outputs = collector.get_outputs()
        # When we provide incomplete input followed by EOF, the REPL tries to read
        # another line, gets EOFError, prints "" and "Goodbye!"
        assert "Goodbye!" in outputs[-1]

    def test_eof_exit(self):
        """Test that EOF causes clean exit."""
        collector = InputCollector([])
        repl(input_fn=collector.input_fn, output_fn=collector.output_fn)
        outputs = collector.get_outputs()
        # Should have banner and "Goodbye!"
        assert "Pebble Lisp REPL" in outputs[0]
        assert "Goodbye!" in outputs[-1]

    def test_custom_env(self):
        """Test REPL with custom environment."""
        env = make_global_env()
        from pebble.types import Symbol
        env.define(Symbol("my-var"), 99)

        collector = InputCollector(["my-var"])
        repl(input_fn=collector.input_fn, output_fn=collector.output_fn, env=env)
        outputs = collector.get_outputs()
        assert "99" in outputs


class TestRunFile:
    """Test the file runner."""

    def test_run_file_basic(self):
        """Test running a basic file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("(define x 42)\n(define y (+ x 8))\n")
            f.flush()
            temp_path = f.name

        try:
            env = run_file(temp_path)
            assert env is not None
            # Check that variables were defined
            from pebble.types import Symbol
            assert env.lookup(Symbol("x")) == 42
            assert env.lookup(Symbol("y")) == 50
        finally:
            os.unlink(temp_path)

    def test_run_file_with_existing_env(self):
        """Test running a file with an existing environment."""
        env = make_global_env()
        from pebble.types import Symbol
        env.define(Symbol("initial"), 10)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("(define result (+ initial 5))\n")
            f.flush()
            temp_path = f.name

        try:
            result_env = run_file(temp_path, env)
            assert result_env is not None
            assert result_env.lookup(Symbol("result")) == 15
        finally:
            os.unlink(temp_path)

    def test_run_file_read_error(self, capsys):
        """Test running a file with read error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("(define x 42\n")  # Missing closing paren
            f.flush()
            temp_path = f.name

        try:
            result = run_file(temp_path)
            assert result is None
            captured = capsys.readouterr()
            assert "error:" in captured.err
        finally:
            os.unlink(temp_path)

    def test_run_file_eval_error(self, capsys):
        """Test running a file with eval error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("(+ 1 undefined-symbol)\n")
            f.flush()
            temp_path = f.name

        try:
            result = run_file(temp_path)
            assert result is None
            captured = capsys.readouterr()
            assert "error:" in captured.err
        finally:
            os.unlink(temp_path)

    def test_run_file_default_env(self):
        """Test that run_file creates a default global env if none provided."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pebble', delete=False) as f:
            f.write("(+ 1 2)\n")
            f.flush()
            temp_path = f.name

        try:
            env = run_file(temp_path)
            assert env is not None
            # Env should have the standard builtins
            from pebble.types import Symbol
            assert callable(env.lookup(Symbol("+")))
        finally:
            os.unlink(temp_path)
