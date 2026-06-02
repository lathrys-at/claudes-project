# Pebble

Pebble is a small Lisp interpreter written in Python — a pebble that grows.

It is being built incrementally. The core is a classic s-expression Lisp:
a reader (tokenizer + parser), an evaluator with a handful of special forms,
a set of primitive builtins, and a REPL.

## Status

- [x] Reader (tokenizer + parser)
- [x] Evaluator + special forms
- [x] Builtins (rich primitive library: arithmetic, predicates, list & string ops, higher-order functions)
- [x] REPL
- [x] Macros & quasiquote
- [ ] Tail-call optimization
- [ ] In-language standard library

## Usage

Start the interactive REPL:

```
python -m pebble
```

Run a script file:

```
python -m pebble path/to/script.pebble
```

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

### Macros

Macros are unhygienic, defmacro-style (like Scheme's non-hygienic macros).
Define macros with `define-macro` in two styles:

```scheme
; Function-style syntax sugar
(define-macro (unless test body)
  `(if ,test nil ,body))

; Value-style with explicit transformer
(define-macro m (lambda (x) `(+ ,x 1)))
```

Macros expand at call time by applying the transformer procedure to unevaluated arguments.
Use `gensym` to generate fresh symbols and avoid variable capture.

### Variadic Parameters

Lambdas and macros support variadic parameters to collect remaining arguments:

```scheme
; Bare symbol collects all arguments
(define sum-all (lambda xs (foldl + 0 xs)))
(sum-all 1 2 3 4)  ; => 10

; Dotted rest syntax for fixed + rest parameters
(define cons-with-prefix (lambda (prefix . rest) (cons prefix rest)))
(cons-with-prefix "x" 1 2)  ; => ("x" 1 2)

; Macros support variadic parameters too
(define-macro (when test . body)
  `(if ,test (begin ,@body) nil))
```
