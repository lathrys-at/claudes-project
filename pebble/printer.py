"""Printer for Pebble values back to Lisp source syntax."""
from pebble.types import Symbol, PebbleList, NIL
from pebble.evaluator import Procedure, Macro


def pebble_repr(value) -> str:
    """Render a Pebble value back into Lisp source syntax (write form).

    Args:
        value: A Pebble value to render.

    Returns:
        A string representation of the value in Lisp syntax.
    """
    # Check for booleans first (before int check, since bool is subclass of int)
    if value is True:
        return "true"
    if value is False:
        return "false"

    # Check for Symbol (before str check, since Symbol is subclass of str)
    if isinstance(value, Symbol):
        return str(value)

    # Check for string (non-Symbol)
    if isinstance(value, str):
        # Escape backslashes, double quotes, and newlines
        escaped = value.replace("\\", "\\\\")
        escaped = escaped.replace('"', '\\"')
        escaped = escaped.replace("\n", "\\n")
        return f'"{escaped}"'

    # Check for int (without bool, since we already handled bool above)
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)

    # Check for float
    if isinstance(value, float):
        return str(value)

    # Check for PebbleList (before checking other types, since it subclasses tuple)
    if isinstance(value, PebbleList):
        if len(value) == 0:
            return "nil"
        else:
            elements = " ".join(pebble_repr(item) for item in value)
            return f"({elements})"

    # Check for Macro
    if isinstance(value, Macro):
        return repr(value)

    # Check for Procedure
    if isinstance(value, Procedure):
        return repr(value)

    # Check for callable (builtin function)
    if callable(value):
        return "<builtin>"

    # Fallback
    return str(value)


def pebble_str(value) -> str:
    """Render a Pebble value to display form (str form).

    Like pebble_repr, but a plain str (non-Symbol) is returned WITHOUT
    surrounding quotes or escaping (its raw text). Everything else is
    the same as pebble_repr.

    Args:
        value: A Pebble value to render.

    Returns:
        A string representation of the value.
    """
    # Check for booleans first (before int check, since bool is subclass of int)
    if value is True:
        return "true"
    if value is False:
        return "false"

    # Check for Symbol (before str check, since Symbol is subclass of str)
    if isinstance(value, Symbol):
        return str(value)

    # Check for string (non-Symbol) - return raw text without quotes
    if isinstance(value, str):
        return value

    # Check for int (without bool, since we already handled bool above)
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)

    # Check for float
    if isinstance(value, float):
        return str(value)

    # Check for PebbleList
    if isinstance(value, PebbleList):
        if len(value) == 0:
            return "nil"
        else:
            elements = " ".join(pebble_repr(item) for item in value)
            return f"({elements})"

    # Check for Macro
    if isinstance(value, Macro):
        return repr(value)

    # Check for Procedure
    if isinstance(value, Procedure):
        return repr(value)

    # Check for callable (builtin function)
    if callable(value):
        return "<builtin>"

    # Fallback
    return str(value)
