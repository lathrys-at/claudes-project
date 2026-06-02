"""Main entry point for Pebble Lisp."""
import sys
from pebble.repl import run_file, repl


def main():
    """Main entry point for the Pebble Lisp CLI."""
    if len(sys.argv) > 1:
        # Run file
        run_file(sys.argv[1])
    else:
        # Run REPL
        repl()


if __name__ == "__main__":
    main()
