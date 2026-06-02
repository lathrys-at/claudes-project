# Pebble

Pebble is a small Lisp interpreter written in Python — a pebble that grows.

It is being built incrementally. The core is a classic s-expression Lisp:
a reader (tokenizer + parser), an evaluator with a handful of special forms,
a set of primitive builtins, and a REPL.

[![CI](https://github.com/lathrys-at/claudes-project/actions/workflows/ci.yml/badge.svg)](https://github.com/lathrys-at/claudes-project/actions/workflows/ci.yml)

**New to Pebble?** Start with [The Pebble Language Guide](docs/GUIDE.md) for a comprehensive tutorial with runnable examples.

## Status

- [x] Reader (tokenizer + parser)
- [x] Evaluator + special forms
- [x] Builtins (rich primitive library: arithmetic, predicates, list & string ops, higher-order functions)
- [x] REPL
- [x] Macros & quasiquote
- [x] Tail-call optimization (tail calls execute in bounded stack space via trampolining)
- [x] In-language standard library

## Installation

Install the package in development mode:

```
pip install -e .
```

This installs the `pebble` console command, allowing you to run Pebble from anywhere on your system.

## Usage

### As a console command

Start the interactive REPL:

```
pebble
```

Run a script file:

```
pebble examples/fizzbuzz.pebble
```

Evaluate a Pebble expression directly:

```
pebble -c "(+ 1 2)"
pebble -c "(sort (list 3 1 2))"
```

### Using `python -m pebble`

Alternatively, you can use the module directly without installing:

```
python -m pebble
python -m pebble path/to/script.pebble
python -m pebble -c "(+ 1 2)"
```

## Running the tests

```
python -m pytest
```

## Examples

Pebble includes a suite of example programs in the `examples/` directory that demonstrate language features end-to-end:

- `examples/fizzbuzz.pebble` — Classic FizzBuzz (1-15) demonstrating recursion and conditionals
- `examples/fibonacci.pebble` — Computes first 10 Fibonacci numbers using tail-recursive helper
- `examples/quicksort.pebble` — Sorts a list using the quicksort algorithm
- `examples/wordcount.pebble` — Counts word frequencies using hash maps
- `examples/error_handling.pebble` — Demonstrates try/catch error handling
- `examples/calculator.pebble` — Arithmetic expression evaluator with operator precedence and parentheses
- `examples/metacircular.pebble` — A tiny Lisp interpreter written in Pebble, supporting lambda, closures, recursion, and define

Run any example directly:

```
python -m pebble examples/fizzbuzz.pebble
```

All examples are covered by tests in `tests/test_examples.py`.

## Design

Pebble values map onto Python values where natural:

| Pebble        | Python                         |
|---------------|--------------------------------|
| integer       | `int`                          |
| float         | `float`                        |
| string        | `str`                          |
| symbol        | `pebble.types.Symbol`          |
| list          | `pebble.types.PebbleList`      |
| hash map      | `pebble.types.PebbleHash`      |
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

### Local Recursion: `letrec` and Named `let`

For local recursive and iterative functions without top-level `define`, Pebble provides two forms:

**`letrec`** creates a scope where multiple names may be mutually recursive:

```scheme
; Single recursion
(letrec ((fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1)))))))
  (fact 5))  ; => 120

; Mutual recursion
(letrec ((even? (lambda (n) (if (= n 0) true (odd? (- n 1)))))
         (odd?  (lambda (n) (if (= n 0) false (even? (- n 1))))))
  (even? 10))  ; => true
```

All initialization expressions and the body are evaluated in the same scope, so each binding can refer to any name (including itself and later-defined names).

**Named `let`** is an idiomatic loop form: `(let NAME (bindings...) body...)` creates a procedure named NAME with parameters matching the binding names, then immediately calls it with the initial values. The procedure can call itself (recursively or iteratively) in the body, and all tail calls are optimized:

```scheme
; Summation loop
(let loop ((i 0) (acc 0))
  (if (= i 5)
    acc
    (loop (+ i 1) (+ acc i))))
; => 10

; Factorial with accumulator
(let fact ((n 5) (acc 1))
  (if (= n 0)
    acc
    (fact (- n 1) (* n acc))))
; => 120
```

Both forms support tail-call optimization, so loops and recursive functions run in bounded stack space even for large iteration counts.

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

### Multi-File Programs: `load`

For larger programs, Pebble supports the `load` special form to evaluate another Pebble source file into the current environment:

```scheme
; Load and evaluate a file
(load "lib.pebble")

; After loading, definitions from the file are available
(my-function 42)

; load returns the value of the last form in the file
(define result (load "compute.pebble"))
```

The `load` special form evaluates all top-level forms in the specified file (relative to the current working directory) in the current environment. Any `define` or `define-macro` in the loaded file becomes immediately visible to the caller, enabling a clean way to organize multi-file programs. The form returns the value of the last form in the loaded file (or `nil` if the file is empty). If the file does not exist or contains syntax errors, an error is raised.

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

### Hash Maps

Pebble includes an immutable hash map (dictionary) data type, perfect for associative key-value storage.
Hash maps are first-class values and support functional, immutable operations:

```scheme
; Create empty hash map
(define m (make-hash))

; Create hash map with initial pairs
(define m (make-hash "name" "Alice" "age" 30 "city" "NYC"))

; Add or update a key (returns new map, original unchanged)
(define m2 (hash-set m "age" 31))

; Look up a key
(hash-ref m "name")               ; => "Alice"
(hash-ref m "missing" "default")  ; => "default" (with default)

; Check for key membership
(hash-has? m "name")              ; => true

; Remove a key (returns new map)
(define m3 (hash-remove m "age"))

; Get size
(hash-count m)                    ; => 3

; Get collections
(hash-keys m)                     ; => ("name" "age" "city")
(hash-values m)                   ; => ("Alice" 30 "NYC")
(hash->list m)                    ; => (("name" "Alice") ("age" 30) ("city" "NYC"))
```

All hash map operations return new maps and leave the originals unchanged (immutability). Keys can be any hashable value: integers, strings, symbols, booleans, and the empty list.

### Standard Library

Pebble includes a standard library written in the Pebble language itself, automatically loaded into the global environment via `make_global_env()`. The library is defined in `pebble/prelude.pebble` and provides:

**Macros:**
- `when` and `unless` — conditional evaluation with optional body forms
- `and` and `or` — short-circuiting logical operators with variadic arity
- `cond` — multi-branch conditional with optional else clause
- `let*` — sequential/nested let bindings
- `case` — pattern matching on literal datums with multiple clauses and optional else
- `while` — tail-call optimized loop while a condition is true
- `dotimes` — tail-call optimized loop iterating over a range of integers

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
- `sort` — returns a new list sorted in ascending order
- `sort-with` — sorts using a custom binary predicate
- `maximum`, `minimum` — largest/smallest element of a non-empty list
- `contains?` — check if element is in list
- `index-of` — returns zero-based index of first occurrence, or -1
- `repeat` — returns a list with element repeated n times
- `assoc` — lookup key in association list

**String functions:**
- `string-join` — join a list of strings with separator
- `string-split` — split string by separator into a list of substrings
- `flatten` — flatten arbitrarily-nested lists

**I/O:**
- `displayln` — display with newline

The prelude is loaded by default and cached, so repeated calls to `make_global_env()` do not re-parse the file. Pass `load_prelude=False` to `make_global_env()` to get an environment with only primitive builtins.
