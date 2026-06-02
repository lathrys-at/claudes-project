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
- [x] Tail-call optimization (tail calls execute in bounded stack space via trampolining)
- [x] In-language standard library

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

### Function Definitions

The `define` special form supports a function-definition shorthand in addition to the standard value form:

```scheme
; Value-style: bind a value to a name
(define x 42)

; Function-definition shorthand: equivalent to (define f (lambda (a b) (+ a b)))
(define (f a b)
  (+ a b))

; The shorthand supports variadic parameters just like lambda
(define (sum . xs)
  (foldl + 0 xs))

(define (map-with-prefix prefix . items)
  (map (lambda (x) (cons prefix x)) items))
```

The shorthand returns the function name symbol. Functions defined this way are tail-call optimized,
and the function's own name is in scope within its body, allowing recursion.

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

### Error Handling

Pebble supports try/catch error handling through the `try` special form:

```scheme
; Basic error catching
(try (error "something went wrong") (catch e e))
; => "something went wrong"

; Catch runtime errors like division by zero
(try (/ 1 0) (catch err (string-append "Error: " err)))
; => "Error: division by zero"

; Handle multiple handler forms
(try (error "oops") (catch e 
  (displayln "Error occurred")
  (string-append "caught: " e)))
; => "caught: oops"
```

The `try` form evaluates a protected expression. If evaluation succeeds, the `try` form returns the value of the expression. If any Pebble evaluation error occurs (from the `error` builtin, division by zero, car on an empty list, undefined symbols, arity mismatches, etc.), the `catch` handler is evaluated instead. The catch clause binds the error's message (a string) to a variable name scoped to the handler only. Multiple forms in the handler are evaluated in order, and the value of the last form is returned. If the handler is empty, `nil` is returned.

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

### Standard Library

Pebble includes a standard library written in the Pebble language itself, automatically loaded into the global environment via `make_global_env()`. The library is defined in `pebble/prelude.pebble` and provides:

**Macros:**
- `when` and `unless` — conditional evaluation with optional body forms
- `and` and `or` — short-circuiting logical operators with variadic arity
- `cond` — multi-branch conditional with optional else clause
- `let*` — sequential/nested let bindings

**List accessors:**
- `caar`, `cadr`, `caddr`, `cddr` — classic nested car/cdr combinations
- `first`, `second`, `third`, `rest` — ordinal list element access

**Basic functions:**
- `identity` — returns its argument
- `inc`, `dec` — increment and decrement by 1
- `zero?`, `positive?`, `negative?`, `even?`, `odd?` — numeric predicates

**Higher-order functions:**
- `compose` — function composition `(compose f g)` → `(lambda (x) (f (g x)))`
- `const` — returns a constant function

**List operations:**
- `last` — last element of a list
- `nth` — zero-indexed element access
- `range` — lazy or eager integer ranges; supports both tail-call optimization and large ranges
- `take`, `drop` — prefix/suffix operations
- `sum`, `product` — aggregate numeric lists
- `reduce` — left fold over non-empty lists
- `map2` — two-argument map (parallel iteration)
- `zip` — pair corresponding elements

**String functions:**
- `string-join` — join a list of strings with separator
- `flatten` — flatten arbitrarily-nested lists

**I/O:**
- `displayln` — display with newline

The prelude is loaded by default and cached, so repeated calls to `make_global_env()` do not re-parse the file. Pass `load_prelude=False` to `make_global_env()` to get an environment with only primitive builtins.
