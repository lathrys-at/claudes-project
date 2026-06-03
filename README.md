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
- `examples/pascal.pebble` — Pascal's triangle generator
- `examples/quicksort.pebble` — Sorts a list using the quicksort algorithm
- `examples/bst.pebble` — Immutable binary search tree built with `define-record`
- `examples/bfs.pebble` — Breadth-first search shortest-path finder over a hash-map graph
- `examples/bank_account.pebble` — Stateful bank account object using closures and `set!` for mutable state
- `examples/collatz.pebble` — Computes the Collatz sequence (3n+1 problem) with stack-safe tail recursion
- `examples/wordcount.pebble` — Counts word frequencies using hash maps
- `examples/number_words.pebble` — Converts integers (0-9999) to their English word representation
- `examples/error_handling.pebble` — Demonstrates try/catch error handling
- `examples/edit_distance.pebble` — Levenshtein edit distance via dynamic programming on a mutable vector
- `examples/hanoi.pebble` — Towers of Hanoi solver returning the sequence of moves
- `examples/calculator.pebble` — Arithmetic expression evaluator with operator precedence and parentheses
- `examples/cipher.pebble` — Caesar cipher / ROT13 text transformer
- `examples/vigenere.pebble` — Vigenère polyalphabetic cipher with key cycling and case preservation
- `examples/metacircular.pebble` — A tiny Lisp interpreter written in Pebble, supporting lambda, closures, recursion, and define
- `examples/json.pebble` — JSON (subset) parser and serializer for objects, arrays, strings, integers, and booleans
- `examples/matrix.pebble` — A small matrix library: transpose, multiply, add, identity
- `examples/life.pebble` — Conway's Game of Life on a mutable-vector grid
- `examples/simplify.pebble` — Symbolic algebra simplifier using `match` pattern-matching to rewrite arithmetic expressions
- `examples/rpn.pebble` — Reverse Polish Notation calculator using a vector as a stack
- `examples/streams.pebble` — Lazy infinite streams library built on `delay`/`force` promises
- `examples/primes.pebble` — Infinite stream of primes via a lazy Sieve of Eratosthenes
- `examples/brainfuck.pebble` — Brainfuck interpreter using a mutable-vector memory tape
- `examples/heap.pebble` — Binary min-heap (priority queue) backed by a mutable vector with heapsort
- `examples/tictactoe.pebble` — Tic-tac-toe win detection checking rows, columns, and diagonals
- `examples/queue.pebble` — Immutable FIFO queue using the two-list (banker's queue) technique

Run any example directly:

```
python -m pebble examples/fizzbuzz.pebble
```

All examples are covered by tests in `tests/test_examples.py`, `tests/test_bst.py`, `tests/test_bfs.py`, `tests/test_bank_account.py`, `tests/test_collatz.py`, `tests/test_edit_distance.py`, `tests/test_hanoi.py`, `tests/test_json.py`, `tests/test_matrix.py`, `tests/test_rpn.py`, `tests/test_streams.py`, `tests/test_primes.py`, `tests/test_brainfuck.py`, `tests/test_heap.py`, `tests/test_metacircular.py`, `tests/test_cipher.py`, `tests/test_vigenere.py`, `tests/test_number_words.py`, and `tests/test_queue.py`.

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
| vector        | `pebble.types.PebbleVector`    |
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

### Pattern Matching with `match`

Pebble provides the `match` macro for recursive pattern matching over nested data structures. The macro dispatches on the first matching clause and binds all pattern variables in the clause body.

```scheme
; Basic variable binding
(match 42
  (x (+ x 1)))                    ; => 43

; Wildcard (matches anything, no binding)
(match (list 1 2)
  (_ "ignored"))                  ; => "ignored"

; Fixed-length list patterns with recursive binding
(match (list 1 (list 2 3))
  ((a (b c)) (+ a b c)))          ; => 6, binds a=1, b=2, c=3

; Quoted-symbol patterns for tagged dispatch
(match (list (quote add) 3 4)
  (((quote add) x y) (+ x y))     ; => 7
  (((quote sub) x y) (- x y)))

; Tail patterns with . REST
(match (list 1 2 3 4)
  ((first . rest) rest))          ; => (2 3 4), binds first=1, rest=(2 3 4)

; Literal elements in patterns
(match (list 1 2)
  ((1 x) (+ x 10)))               ; => 12, matches only if first element is 1
```

A pattern matches a value recursively as follows:
- `_` — matches any value, binds nothing
- Symbol (not `_`) — matches any value, binds the symbol to the value
- `(quote SYM)` — matches iff the value equals the symbol SYM (used for tagged dispatch)
- Literal (number, string, boolean) — matches iff the value equals the literal
- `nil` — matches iff the value is the empty list
- `(P1 P2 ... Pn)` — fixed list pattern; matches iff the value is a list of exactly length n and each element matches its corresponding pattern Pi recursively
- `(P1 ... Pn . REST)` — tail pattern; matches iff the value is a list of length ≥ n, first n elements match P1...Pn recursively, and REST (a symbol) is bound to the list of remaining elements

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

; Functional hash map helpers (standard library)
; Update a value by applying a function
(hash-update m "age" inc 30)      ; => {"name" "Alice" "age" 31 "city" "NYC"}

; Merge two maps (values from second map win on key conflicts)
(hash-merge m (make-hash "age" 31 "country" "US"))  
                                  ; => {"name" "Alice" "age" 31 "city" "NYC" "country" "US"}

; Transform all values with a function
(hash-map-values (lambda (v) (+ v 1)) (make-hash "a" 1 "b" 2))
                                  ; => {"a" 2 "b" 3}

; Filter entries by key and value predicate
(hash-filter (lambda (k v) (> v 25)) m)
                                  ; => {"age" 30}
```

All hash map operations return new maps and leave the originals unchanged (immutability). Keys can be any hashable value: integers, strings, symbols, booleans, and the empty list.

**Standard library hash map helpers:**
- `hash-update` — `(hash-update m k f default)` returns a new map where key `k` is mapped to `(f current)`, where `current` is the current value for `k` in `m`, or `default` if `k` is absent. Useful for counting and accumulation idioms.
- `hash-merge` — `(hash-merge m1 m2)` returns a new map containing all entries from both `m1` and `m2`. When a key appears in both, the value from `m2` wins. Neither input is modified.
- `hash-map-values` — `(hash-map-values f m)` returns a new map with the same keys as `m`, but each value `v` is replaced by `(f v)`. Useful for transforming all values uniformly.
- `hash-filter` — `(hash-filter pred m)` returns a new map containing only entries `(k v)` where `(pred k v)` is truthy. The predicate receives both key and value as arguments.
- `frequencies` — `(frequencies lst)` returns a hash map mapping each distinct element of `lst` to the number of times it occurs. Useful for frequency analysis and counting occurrences.
- `group-by` — `(group-by f lst)` returns a hash map mapping each distinct key `(f x)` to a list of all elements `x` from `lst` that produced that key, with elements in their original relative order. Useful for partitioning data by computed keys.

### Mutable Vectors

Pebble includes a mutable vector (array) data type for dynamic, in-place sequence manipulation.
Unlike Pebble lists and hash maps (which are immutable), vectors support mutation and are useful for algorithms requiring efficient dynamic arrays:

```scheme
; Create vectors
(define v (vector 1 2 3))           ; => #(1 2 3)
(define v (make-vector 5 0))        ; => #(0 0 0 0 0) (5 elements, filled with 0)
(define v (make-vector 3))          ; => #(nil nil nil) (filled with nil by default)

; Access elements
(vector-ref v 0)                    ; => 1
(vector-length v)                   ; => 3

; Mutate in place (visible through all references)
(vector-set! v 0 99)                ; => nil (returns nil, modifies v)
(vector-ref v 0)                    ; => 99

; Dynamic growth
(vector-push! v 4)                  ; => nil (appends 4, grows vector by 1)
(vector-length v)                   ; => 4

; Stack operations (vectors as LIFO stacks)
(vector-last v)                     ; => 4 (peek at last element, doesn't modify)
(vector-pop! v)                     ; => 4 (remove and return last element)
(vector-length v)                   ; => 3 (shrinks after pop)

; Conversions
(vector->list v)                    ; => (99 2 3) (creates immutable list)
(list->vector (list 1 2 3))         ; => #(1 2 3) (creates mutable vector)

; Testing and predicates
(vector? v)                         ; => true
(vector? (list 1 2))               ; => false
```

Vectors are mutable, meaning `vector-set!` changes the vector in place and is visible through all references to that vector (true reference semantics). An empty vector `#()` is still truthy (only `false` and the empty list are falsy).

### Primitive Builtins

Pebble provides a comprehensive set of primitive builtin functions implemented in Python:

**Arithmetic Operations:**
- `+`, `-`, `*`, `/` — basic arithmetic (variadic for `+`, `*`; `-` supports unary negation)
- `abs` — absolute value
- `expt` — exponentiation (base, exponent)
- `min`, `max` — minimum and maximum (variadic)
- `modulo` — remainder of division (sign follows divisor)
- `quotient` — integer division truncated toward zero
- `remainder` — remainder of truncating division (sign follows dividend)
- `gcd` — greatest common divisor (variadic)
- `lcm` — least common multiple (variadic)

**Bitwise Operations:**
- `bit-and` — bitwise AND of integer arguments (variadic; `(bit-and)` returns -1, the identity)
- `bit-or` — bitwise OR of integer arguments (variadic; `(bit-or)` returns 0, the identity)
- `bit-xor` — bitwise XOR of integer arguments (variadic; `(bit-xor)` returns 0, the identity)
- `bit-not` — bitwise complement (logical NOT, returns ~n)
- `arithmetic-shift` — shift n left by k bits if k ≥ 0, right (signed) if k < 0

**Floating-Point Operations:**
- `sqrt` — square root (returns float)
- `floor` — largest integer ≤ x
- `ceiling` — smallest integer ≥ x
- `round` — nearest integer (banker's rounding)
- `truncate` — integer part toward zero

**Comparison:**
- `=`, `<`, `>`, `<=`, `>=` — comparison operators (variadic, chained)

**Type Predicates:**
- `number?`, `integer?`, `float?` — numeric type checks
- `string?`, `symbol?` — string and symbol checks
- `list?`, `pair?`, `null?`, `nil?` — list checks (pair? is non-empty, null?/nil? are empty)
- `boolean?`, `procedure?` — boolean and function checks
- `vector?`, `hash?` — collection type checks

**Boolean:**
- `not` — logical negation

**List Operations:**
- `list`, `cons` — list construction
- `car`, `cdr` — head and tail access
- `length` — list length
- `append` — concatenate lists
- `reverse` — reverse a list
- `list-ref` — element at index
- `member` — find element in list

**Higher-Order Functions:**
- `map`, `filter` — transform and select list elements
- `foldl`, `foldr` — left and right folds (accumulation)
- `for-each` — apply function for side effects
- `apply` — apply function to list of arguments

**Vector Operations:**
- `vector`, `make-vector` — vector construction
- `vector-ref`, `vector-set!` — access and mutation
- `vector-length` — vector length
- `vector->list`, `list->vector` — conversions
- `vector-push!` — append to vector
- `vector-pop!` — remove and return the last element (raises error if empty)
- `vector-last` — return the last element without modifying (raises error if empty)
- `vector-map` — apply function to each element and return new vector
- `vector-for-each` — apply function to each element for side effects
- `vector-copy` — create an independent copy of a vector
- `vector-fill!` — fill every element of a vector with a value

**String Operations:**
- `string-append` — concatenate strings
- `string-length` — string length
- `substring` — extract substring
- `format` — templated string construction with directives (~a, ~s, ~%, ~~)
- `string-upcase` — convert to uppercase
- `string-downcase` — convert to lowercase
- `string-contains?` — check if substring is contained in string
- `string-index` — find first index of substring (or -1 if not found)
- `string-prefix?` — check if string starts with prefix
- `string-suffix?` — check if string ends with suffix
- `string-repeat` — repeat string n times
- `string-replace` — replace all occurrences of substring
- `string-trim` — remove leading and trailing whitespace
- `char-at` — get character at index as a one-character string
- `string->list` — convert string to list of one-character strings
- `list->string` — concatenate list of strings
- `string->symbol`, `symbol->string` — conversions
- `number->string`, `string->number` — numeric conversions

**Character Classification and Conversion:**
- `char-numeric?` — test if character is a decimal digit
- `char-alpha?` — test if character is an alphabetic character
- `char-whitespace?` — test if character is a whitespace character (space, tab, newline, etc.)
- `char-upcase` — convert character to uppercase (non-letters unchanged)
- `char-downcase` — convert character to lowercase (non-letters unchanged)
- `char->integer` — get Unicode code point of a character
- `integer->char` — create character from Unicode code point

**Hash Map Operations:**
- `make-hash` — create hash map
- `hash-set` — add/update key (immutable)
- `hash-ref` — look up value by key
- `hash-has?` — check key membership
- `hash-remove` — remove key (immutable)
- `hash-count` — number of entries
- `hash-keys`, `hash-values` — get keys and values as lists
- `hash->list` — convert to list of [key value] pairs

**I/O:**
- `print`, `display` — output with or without newline
- `newline` — output newline

**Error Handling & Meta:**
- `error` — raise an EvalError
- `gensym` — generate unique symbols (for macros)
- `macro?` — test if value is a macro

### Standard Library

Pebble includes a standard library written in the Pebble language itself, automatically loaded into the global environment via `make_global_env()`. The library is defined in `pebble/prelude.pebble` and provides:

**Macros:**
- `when` and `unless` — conditional evaluation with optional body forms
- `if-let` and `when-let` — ergonomic binding macros for conditionals with optional values
- `and` and `or` — short-circuiting logical operators with variadic arity
- `cond` — multi-branch conditional with optional else clause
- `let*` — sequential/nested let bindings
- `case` — pattern matching on literal datums with multiple clauses and optional else
- `match` — recursive pattern matching with full pattern grammar (see below)
- `while` — tail-call optimized loop while a condition is true
- `dotimes` — tail-call optimized loop iterating over a range of integers
- `define-record` — defines user-defined mutable record types with constructor, predicate, accessors, and mutators

**List accessors:**
- `caar`, `cadr`, `caddr`, `cddr` — classic nested car/cdr combinations
- `first`, `second`, `third`, `rest` — ordinal list element access

**Basic functions:**
- `identity` — returns its argument
- `inc`, `dec` — increment and decrement by 1
- `zero?`, `positive?`, `negative?`, `even?`, `odd?` — numeric predicates

**Numeric base conversion:**
- `number->base` — `(number->base n base)` converts a non-negative integer `n` to its string representation in the given `base` (an integer from 2 to 16 inclusive), using lowercase digits `0-9a-f`
- `base->number` — `(base->number s base)` parses the string `s` as a non-negative integer written in `base` (2-16) and returns that integer
- `number->binary` — `(number->binary n)` converts a non-negative integer to its binary (base 2) string representation
- `number->hex` — `(number->hex n)` converts a non-negative integer to its hexadecimal (base 16) string representation
- `binary->number` — `(binary->number s)` parses a binary string and returns the integer value
- `hex->number` — `(hex->number s)` parses a hexadecimal string and returns the integer value

**Digit manipulation:**
- `digits` — `(digits n)` returns a list of the decimal digits of a non-negative integer `n`, in order from most significant (left) to least significant (right). For example, `(digits 12345)` → `(1 2 3 4 5)`. `(digits 0)` → `(0)`. `(digits 100)` → `(1 0 0)`. Raises an error if `n` is not an integer or is negative.
- `digit-sum` — `(digit-sum n)` returns the sum of the decimal digits of a non-negative integer `n`. Equivalent to `(sum (digits n))`. For example, `(digit-sum 12345)` → `15` (1+2+3+4+5), `(digit-sum 99)` → `18`. Raises an error if `n` is not an integer or is negative.
- `digital-root` — `(digital-root n)` returns the digital root of a non-negative integer `n`: the single digit obtained by repeatedly summing the digits until a value in the range 0-9 is reached. For example, `(digital-root 12345)` → `6` (digits sum to 15, then 1+5=6), `(digital-root 9875)` → `2` (29 → 11 → 2). `(digital-root 0)` → `0`. For single-digit inputs (0-9), returns the input unchanged. Raises an error if `n` is not an integer or is negative.

**Roman numeral conversion:**
- `int->roman` — `(int->roman n)` converts an integer `n` (where 1 ≤ n ≤ 3999) to its Roman numeral string representation using standard subtractive notation (e.g., `(int->roman 944)` → `"CMXLIV"`). Raises an error if `n` is not an integer or is outside the valid range.
- `roman->int` — `(roman->int s)` parses a Roman numeral string `s` and returns the integer value. Implements the standard left-to-right scanning rule: each letter's value is added, except when a letter's value is less than the letter immediately following it, in which case it is subtracted (e.g., `(roman->int "CMXLIV")` → `944`). Letter values: I=1, V=5, X=10, L=50, C=100, D=500, M=1000.

**Combinatorics:**
- `factorial` — `(factorial n)` returns `n!` for a non-negative integer `n`. `(factorial 0)` is 1. Implemented tail-recursively with an accumulator, so it handles large `n` without stack overflow. Works with arbitrary-precision integers. Raises an error if `n` is not an integer or is negative. Example: `(factorial 5)` → `120`, `(factorial 13)` → `6227020800`
- `permutations-count` — `(permutations-count n k)` returns the number of k-permutations of n (ordered selections of k items from n items): `n! / (n-k)!`. Requires non-negative integers `n` and `k`. If `k > n`, returns 0. `(permutations-count n 0)` is 1. Uses exact integer arithmetic. Raises an error if `n` or `k` is not an integer or is negative. Example: `(permutations-count 5 2)` → `20`, `(permutations-count 10 3)` → `720`
- `combinations-count` — `(combinations-count n k)` returns the binomial coefficient "n choose k" (unordered selections of k items from n items): `n! / (k! * (n-k)!)`. Requires non-negative integers `n` and `k`. If `k > n`, returns 0. `(combinations-count n 0)` and `(combinations-count n n)` are 1. Uses exact integer arithmetic. Raises an error if `n` or `k` is not an integer or is negative. Example: `(combinations-count 5 2)` → `10`, `(combinations-count 52 5)` → `2598960`

**List combinatorics:**
- `permutations` — `(permutations lst)` returns a list of all permutations (orderings) of the elements of `lst`. Each permutation is a list. The result is a list of lists. `(permutations nil)` returns `(())` (a one-element list containing the empty list). For a list of n distinct elements, there are n! permutations. For example, `(length (permutations (list 1 2 3)))` → `6`. The exact order of permutations in the result is unspecified, but every permutation appears exactly once.
- `power-set` — `(power-set lst)` returns a list of all subsets (the power set) of `lst`. Each subset is a list. The result is a list of lists. `(power-set nil)` returns `(())` (a one-element list containing the empty list). For a list of n elements, there are 2^n subsets. For example, `(length (power-set (list 1 2 3)))` → `8`, and the result contains `nil` (the empty subset), all singletons, all pairs, and the full set. The exact order of subsets in the result is unspecified, but every subset appears exactly once.

**Number theory:**
- `prime?` — `(prime? n)` returns true if `n` is a prime number, false otherwise. A number is prime iff it is an integer ≥ 2 with no divisors `d` where `2 ≤ d` and `d*d ≤ n`. Uses trial division up to the square root for efficient checking. Returns false for all integers less than 2 and for non-integers. Example: `(prime? 2)` → `true`, `(prime? 97)` → `true`, `(prime? 91)` → `false` (since 91 = 7 × 13)
- `primes-up-to` — `(primes-up-to n)` returns a list of all prime numbers less than or equal to `n`, in ascending order. For `n < 2`, returns the empty list. Implemented by filtering `prime?` over the range from 2 to n. Example: `(primes-up-to 10)` → `(2 3 5 7)`, `(primes-up-to 30)` → `(2 3 5 7 11 13 17 19 23 29)`, `(length (primes-up-to 100))` → `25`

**Higher-order functions:**
- `compose` — function composition `(compose f g)` → `(lambda (x) (f (g x)))`
- `const` — returns a constant function
- `partial` — partial application; `(partial f arg1 arg2 ...)` returns a new function that, when called with additional arguments, calls `f` with the fixed arguments followed by the additional arguments. Example: `((partial + 10) 5)` → `15`
- `flip` — argument swapper; `(flip f)` returns a two-argument function that swaps the arguments to `f`. Example: `((flip -) 3 10)` → `7` (computes `10 - 3`)
- `complement` — logical negation wrapper; `(complement pred)` returns a function that applies `pred` to the same arguments and returns the boolean negation. Works for predicates of any arity. Example: `((complement even?) 3)` → `true`
- `memoize` — caching decorator; `(memoize f)` returns a new function that caches results per distinct argument list, invoking the underlying function at most once per unique argument sequence

**List operations:**
- `last` — last element of a list
- `nth` — zero-indexed element access
- `range` — lazy or eager integer ranges; supports both tail-call optimization and large ranges
- `iterate` — `(iterate f x n)` returns a list of `n` elements by repeatedly applying function `f`: `x`, `(f x)`, `(f (f x))`, ..., `(f^(n-1) x)`. For `n = 0`, returns the empty list. Stack-safe for large `n`. Example: `(iterate (lambda (v) (* v 2)) 1 5)` → `(1 2 4 8 16)`
- `range-step` — `(range-step start stop step)` returns an arithmetic sequence starting at `start` with a common difference of `step`. If `step` is positive, includes values while `value < stop`; if negative, includes values while `value > stop`. The endpoint `stop` is exclusive. `step` must be nonzero (raises an error otherwise). Stack-safe for large ranges. Examples: `(range-step 0 10 2)` → `(0 2 4 6 8)`, `(range-step 10 0 -2)` → `(10 8 6 4 2)`
- `take`, `drop` — prefix/suffix operations
- `take-while` — longest prefix of list whose elements satisfy a predicate
- `drop-while` — list with leading elements satisfying predicate removed
- `chunk` — `(chunk lst n)` splits a list into consecutive sublists of length n, returning a list of chunks. The last chunk may be shorter if the list length is not a multiple of n. Empty list yields empty list. Stack-safe for large lists.
- `interleave` — `(interleave a b)` returns a list alternating elements from lists `a` and `b`, stopping when either list runs out. Stack-safe for large lists.
- `enumerate` — `(enumerate lst)` returns a list of two-element lists pairing each element with its zero-based index: `((0 elem0) (1 elem1) ...)`. Stack-safe for large lists.
- `find` — first element satisfying a predicate, or false if none found
- `any?` — true iff at least one element satisfies a predicate
- `all?` — true iff every element satisfies a predicate (vacuously true for empty list)
- `count-if` — count of elements satisfying a predicate
- `partition` — split list into two: elements satisfying predicate and those that don't
- `sum`, `product` — aggregate numeric lists
- `reduce` — left fold over non-empty lists
- `map2` — two-argument map (parallel iteration)
- `zip` — pair corresponding elements
- `sort` — returns a new list sorted in ascending order
- `sort-with` — sorts using a custom binary predicate
- `maximum`, `minimum` — largest/smallest element of a non-empty list
- `mean` — `(mean lst)` returns the arithmetic mean (average) of a non-empty list of numbers: `(sum lst) / (length lst)`. Raises an error on the empty list.
- `median` — `(median lst)` returns the median of a non-empty list of numbers. Sorts the list internally; if the length is odd, returns the middle element; if even, returns the average of the two middle elements. Does not mutate the input. Raises an error on the empty list.
- `variance` — `(variance lst)` returns the population variance of a non-empty list of numbers: the mean of the squared deviations from the mean `(sum of (xi - mean)^2) / length`. Raises an error on the empty list.
- `stddev` — `(stddev lst)` returns the population standard deviation of a non-empty list of numbers: `(sqrt (variance lst))`. Raises an error on the empty list.
- `contains?` — check if element is in list
- `index-of` — returns zero-based index of first occurrence, or -1
- `repeat` — returns a list with element repeated n times
- `assoc` — lookup key in association list

**Run-length encoding:**
- `rle-encode` — `(rle-encode lst)` returns the run-length encoding of a list, converting each maximal run of consecutive equal elements into a `(element count)` pair. The encoding is a list of such pairs in order, preserving element positions. `(rle-encode nil)` returns the empty list. Stack-safe implementation using accumulator-based tail recursion. Example: `(rle-encode (list 1 1 1 2 3 3))` → `((1 3) (2 1) (3 2))`
- `rle-decode` — `(rle-decode encoded)` returns the original list from a run-length encoding, expanding each `(element count)` pair into `count` copies of `element`, concatenated in order. `(rle-decode nil)` returns the empty list. Example: `(rle-decode (list (list 1 3) (list 2 1) (list 3 2)))` → `(1 1 1 2 3 3)`. Works with any elements comparable via `=`, including strings and symbols.

**Set operations on lists:**
- `unique` — `(unique lst)` returns a list with duplicate elements removed, preserving the order of first appearance of each element
- `union` — `(union a b)` returns the set union of two lists: distinct elements from both, with elements from `a` first (in their original order), followed by elements from `b` not in `a`
- `intersection` — `(intersection a b)` returns the distinct elements that appear in both `a` and `b`, in the order they appear in `a`
- `difference` — `(difference a b)` returns the distinct elements of `a` that do not appear in `b`, in the order they appear in `a`

**Vector functions (standard library):**
- `vector-map` — `(vector-map f v)` returns a new vector where each element is `(f (vector-ref v i))` for index i. The original vector `v` is not modified.
- `vector-for-each` — `(vector-for-each f v)` applies `(f element)` to each element of `v` in order for side effects, returning `nil`.
- `vector-copy` — `(vector-copy v)` returns an independent copy of vector `v` with the same elements. Mutating the copy does not affect the original, and vice versa.
- `vector-fill!` — `(vector-fill! v x)` sets every element of `v` to `x` in place, mutating the vector. The change is visible through all references to `v`, and the function returns `nil`.
- `binary-search` — `(binary-search vec target)` performs binary search over an ascending-sorted vector `vec` for `target`, returning the 0-based index where `target` is found, or `-1` if `target` is not present. Uses tail-recursive iteration for stack-safety. Assumes `vec` is sorted in ascending order. Example: `(binary-search (vector 1 3 5 7 9) 5)` → `2`, `(binary-search (vector 1 3 5 7 9) 4)` → `-1`

**Lazy evaluation (promises):**
- `delay` — `(delay EXPR)` is a macro that creates a promise representing the deferred computation of `EXPR`. The expression is NOT evaluated immediately; it is captured in the current lexical environment and only evaluated when the promise is forced.
- `force` — `(force P)` forces a promise P. If P is a promise, the first force evaluates the deferred expression and caches the result; subsequent forces return the cached value without re-evaluating. If P is not a promise, it is returned unchanged.
- `promise?` — `(promise? x)` returns true if x is a promise created by `delay`, and false for all other values. Example:
  ```lisp
  (define p (delay (+ 1 2)))
  (promise? p)              ; true
  (force p)                 ; 3
  (force p)                 ; 3 (cached, expression not re-evaluated)
  (promise? 5)              ; false
  ```

**Lazy streams:**
Pebble includes a lazy streams library built on `delay`/`force` promises. A lazy stream is either `nil` (empty) or a two-element list `(list HEAD (delay REST))` where `HEAD` is the first element and `REST` is a promise wrapping the rest of the stream. Streams are evaluated lazily: the tail is not computed until accessed, enabling infinite streams.
- `stream-cons` — `(stream-cons HEAD TAIL)` is a macro that creates a stream with `HEAD` (evaluated now) and `TAIL` (delayed). Must be a macro so `TAIL` is not eagerly evaluated.
- `stream-car` — `(stream-car s)` returns the head (first element) of a stream.
- `stream-cdr` — `(stream-cdr s)` forces the delayed tail and returns the next stream.
- `stream-null?` — `(stream-null? s)` returns true iff `s` is the empty stream (the empty list).
- `stream-take` — `(stream-take s n)` returns an ordinary Pebble list of the first `n` elements of stream `s` (or fewer if the stream ends earlier). `(stream-take s 0)` returns the empty list.
- `stream-ref` — `(stream-ref s i)` returns the i-th element (0-indexed) of the stream, advancing through the stream as needed.
- `stream-map` — `(stream-map f s)` returns a new stream lazily applying `f` to each element of `s`.
- `stream-filter` — `(stream-filter pred s)` returns a stream of the elements of `s` that satisfy the predicate `pred` (lazily).
- `stream-zip-with` — `(stream-zip-with f s1 s2)` returns a stream whose i-th element is `(f a_i b_i)` for the i-th elements of `s1` and `s2`, stopping when either stream is empty.
- `integers-from` — `(integers-from n)` returns the infinite stream `n, n+1, n+2, ...`. Works because the tail is delayed inside the promise, so the stream builds lazily without infinite recursion. Example:
  ```lisp
  (stream-take (integers-from 1) 5)              ; => (1 2 3 4 5)
  (stream-take (stream-map (lambda (x) (* x x)) (integers-from 1)) 5)  ; => (1 4 9 16 25)
  (stream-take (stream-filter even? (integers-from 1)) 4)             ; => (2 4 6 8)
  (stream-take (stream-zip-with + (integers-from 1) (integers-from 100)) 3)  ; => (101 103 105)
  ```

**String functions:**
- `string-join` — join a list of strings with separator
- `string-split` — split string by separator into a list of substrings
- `string-reverse` — return string with characters in reverse order
- `capitalize` — return string with first character uppercased and rest unchanged
- `string-pad-left` — pad string on the left to a given width with a fill character
- `string-pad-right` — pad string on the right to a given width with a fill character
- `words` — `(words s)` splits the string `s` on runs of whitespace (spaces, tabs, newlines) into a list of non-empty words. Leading, trailing, and repeated whitespace are ignored and produce no empty strings. A string with no words (empty or all whitespace) yields nil. Example: `(words "  hello   world  ")` → `("hello" "world")`
- `unwords` — `(unwords lst)` joins a list of strings with single spaces between them. The empty list yields an empty string. Example: `(unwords (list "hello" "world"))` → `"hello world"`
- `lines` — `(lines s)` splits the string `s` on newline characters `\n` into a list of line strings, preserving empty segments. This is equivalent to `(string-split s "\n")`. A trailing newline produces a trailing empty string in the result. Example: `(lines "a\nb\nc")` → `("a" "b" "c")` and `(lines "a\n")` → `("a" "")`
- `unlines` — `(unlines lst)` joins a list of strings with newline characters between them. The empty list yields an empty string. This is equivalent to `(string-join lst "\n")`. Example: `(unlines (list "a" "b" "c"))` → `"a\nb\nc"`
- `flatten` — flatten arbitrarily-nested lists

**I/O:**
- `displayln` — display with newline

**Records (user-defined types):**
- `define-record` — `(define-record NAME (FIELD1 FIELD2 ...))` defines a new record type with a constructor `make-NAME`, predicate `NAME?`, field accessors `NAME-FIELD1`, `NAME-FIELD2`, etc., and field mutators `set-NAME-FIELD1!`, `set-NAME-FIELD2!`, etc. Records are mutable and unforgeable: only values created by the specific constructor satisfy the predicate. Records are represented internally as mutable vectors, so mutations are visible through all references (reference semantics). Example:
  ```lisp
  (define-record point (x y))
  (define p (make-point 3 4))
  (point? p)           ; true
  (point-x p)          ; 3
  (= p (make-point 3 4)) ; true (records with equal fields are equal)
  (set-point-x! p 10)  ; mutate in place, returns nil
  (point-x p)          ; 10
  (define q p)         ; q now aliases p
  (set-point-y! q 20)  ; mutate via q
  (point-y p)          ; 20 (mutation is visible through p as well)
  ```

The prelude is loaded by default and cached, so repeated calls to `make_global_env()` do not re-parse the file. Pass `load_prelude=False` to `make_global_env()` to get an environment with only primitive builtins.
