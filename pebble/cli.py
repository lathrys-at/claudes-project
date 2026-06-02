"""Command-line interface for Pebble Lisp."""
import sys
from pebble.reader import read, ReadError
from pebble.evaluator import seval, make_global_env, eval_source, EvalError
from pebble.printer import pebble_repr


def main(argv=None):
    """Main entry point for the Pebble Lisp CLI.

    Args:
        argv: List of command-line arguments (defaults to sys.argv[1:]).
              Supports:
              - No arguments: start interactive REPL
              - FILE: run a Pebble source file
              - -c EXPR: evaluate a Pebble expression and print the result
    """
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        # No arguments: start REPL
        from pebble.repl import repl
        repl()
    elif argv[0] == "-c":
        # -c mode: evaluate expression
        if len(argv) < 2:
            print("error: -c requires an expression argument", file=sys.stderr)
            sys.exit(1)

        expr = argv[1]
        env = make_global_env()
        try:
            result = eval_source(expr, env)
            print(pebble_repr(result))
        except (ReadError, EvalError) as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # File mode: run the file
        path = argv[0]
        env = make_global_env()
        try:
            with open(path, 'r') as f:
                source = f.read()
            eval_source(source, env)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        except (ReadError, EvalError) as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
