"""Interactive REPL and file runner for Pebble Lisp."""
import sys
from pebble.reader import read, ReadError
from pebble.evaluator import seval, make_global_env, eval_source, EvalError
from pebble.printer import pebble_repr


def run_file(path, env=None):
    """Run a Pebble source file.

    Args:
        path: Path to the file to execute.
        env: The Environment to evaluate in. If None, a global env is created.

    Returns:
        The environment after evaluation, or None on error.
    """
    if env is None:
        env = make_global_env()

    try:
        with open(path, 'r') as f:
            source = f.read()
        eval_source(source, env)
        return env
    except ReadError as e:
        print(f"error: {e}", file=sys.stderr)
        return
    except EvalError as e:
        print(f"error: {e}", file=sys.stderr)
        return


def repl(input_fn=input, output_fn=print, env=None):
    """Interactive read-eval-print loop.

    Args:
        input_fn: Function to read a line (default: input). Should raise EOFError on EOF.
        output_fn: Function to print output (default: print).
        env: The Environment to evaluate in. If None, a global env is created.
    """
    if env is None:
        env = make_global_env()

    output_fn("Pebble Lisp REPL. Ctrl-D to exit.")

    buffer = ""
    while True:
        try:
            # Read a line
            if buffer:
                prompt = "...... "
            else:
                prompt = "pebble> "
            line = input_fn(prompt)
            buffer += line + "\n"

            # Try to parse the buffer
            try:
                forms = read(buffer)
                # Successfully parsed - evaluate all forms
                try:
                    result = None
                    for form in forms:
                        result = seval(form, env)
                    # Print the result of the last form (only if there were forms)
                    if result is not None:
                        output_fn(pebble_repr(result))
                    buffer = ""
                except EvalError as e:
                    # Evaluation error - print and continue
                    output_fn(f"error: {e}")
                    buffer = ""
            except ReadError as e:
                error_msg = str(e)
                # Check if it's an incomplete input error
                if ("Unexpected end of input" in error_msg or
                    "Unbalanced" in error_msg or
                    "Unterminated" in error_msg):
                    # Incomplete, read another line
                    continue
                else:
                    # Other read error
                    output_fn(f"error: {error_msg}")
                    buffer = ""
        except EOFError:
            output_fn("")
            output_fn("Goodbye!")
            return
        except KeyboardInterrupt:
            buffer = ""
