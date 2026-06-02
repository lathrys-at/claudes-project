# Pebble

Pebble is a small Lisp interpreter written in Python — a pebble that grows.

It is being built incrementally. The core is a classic s-expression Lisp:
a reader (tokenizer + parser), an evaluator with a handful of special forms,
a set of primitive builtins, and a REPL.

## Status

- [x] Reader (tokenizer + parser)
- [ ] Evaluator + special forms
- [ ] Builtins
- [ ] REPL
- [ ] Macros & quasiquote
- [ ] Tail-call optimization
- [ ] In-language standard library

## Running the tests

```
python -m pytest
```

## Design

Pebble values map onto Python values where natural:

| Pebble        | Python                         |
|---------------|--------------------------------|
| integer       | `int`                          |
| float         | `float`                        |
| string        | `str`                          |
| symbol        | `pebble.types.Symbol`          |
| list          | `pebble.types.PebbleList`      |
| nil / empty   | empty `PebbleList`             |
| boolean       | `True` / `False`               |
