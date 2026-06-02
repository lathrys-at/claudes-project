"""Core Pebble data types."""
from __future__ import annotations
from typing import Iterable


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


# The canonical empty list / nil.
NIL = PebbleList()
