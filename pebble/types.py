"""Core Pebble data types."""
from __future__ import annotations
from typing import Iterable, Any, Dict


class Symbol(str):
    """A Lisp symbol. Subclasses str so it is hashable and easy to compare,
    but is a distinct type from a Pebble string."""
    __slots__ = ()
    def __repr__(self) -> str:
        return f"Symbol({str.__repr__(self)})"


class PebbleList(tuple):
    """An immutable Lisp list, represented as a tuple of elements."""
    __slots__ = ()
    def __new__(cls, items: Iterable = ()):
        return super().__new__(cls, tuple(items))
    def __repr__(self) -> str:
        return f"PebbleList({tuple.__repr__(self)})"


class PebbleHash:
    """An immutable hash map (dictionary) for Pebble.

    Wraps a Python dict internally. Two PebbleHash instances are equal if they
    contain the same key/value pairs.
    """
    __slots__ = ('_data',)

    def __init__(self, data: Dict[Any, Any] = None):
        """Create a PebbleHash from a dict or empty if None."""
        if data is None:
            self._data = {}
        else:
            self._data = dict(data)  # Make a copy to ensure immutability

    def __repr__(self) -> str:
        return f"PebbleHash({self._data!r})"

    def __eq__(self, other) -> bool:
        """Two PebbleHash instances are equal if their data dicts are equal."""
        if not isinstance(other, PebbleHash):
            return False
        return self._data == other._data

    def __hash__(self):
        """PebbleHash is not hashable (mutable-like interface)."""
        raise TypeError("unhashable type: 'PebbleHash'")

    def get(self, key, default=None):
        """Get value by key, returning default if absent."""
        return self._data.get(key, default)

    def __contains__(self, key) -> bool:
        """Check if key is in hash map."""
        return key in self._data

    def __len__(self) -> int:
        """Return number of key/value pairs."""
        return len(self._data)

    def keys(self):
        """Return keys view."""
        return self._data.keys()

    def values(self):
        """Return values view."""
        return self._data.values()

    def items(self):
        """Return items view."""
        return self._data.items()


class PebbleVector:
    """A mutable vector (array) for Pebble.

    Wraps a Python list internally. Two PebbleVector instances are equal if they
    currently contain the same elements in the same order (via ==).
    """
    __slots__ = ('_data',)

    def __init__(self, items: Iterable = ()):
        """Create a PebbleVector from an iterable."""
        self._data = list(items)

    def __repr__(self) -> str:
        return f"PebbleVector({self._data!r})"

    def __eq__(self, other) -> bool:
        """Two PebbleVector instances are equal if their current data is equal."""
        if not isinstance(other, PebbleVector):
            return False
        return self._data == other._data

    def __hash__(self):
        """PebbleVector is not hashable (mutable)."""
        raise TypeError("unhashable type: 'PebbleVector'")

    def __len__(self) -> int:
        """Return length of vector."""
        return len(self._data)

    def __getitem__(self, index):
        """Get element at index."""
        return self._data[index]

    def __setitem__(self, index, value):
        """Set element at index (for internal use)."""
        self._data[index] = value

    def append(self, value):
        """Append value to the end of the vector."""
        self._data.append(value)

    def pop(self):
        """Remove and return the last element of the vector."""
        return self._data.pop()


# The canonical empty list / nil.
NIL = PebbleList()
