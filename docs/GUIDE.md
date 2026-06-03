# The Pebble Language Guide

Pebble is a small Lisp interpreter written in Python. This guide teaches you the language from scratch, covering data types, special forms, macros, functions, error handling, and the standard library.

## Table of Contents

1. [Installation and Running Code](#installation-and-running-code)
2. [Data Types](#data-types)
3. [Evaluation and Quoting](#evaluation-and-quoting)
4. [Control Flow](#control-flow)
5. [Defining Values and Functions](#defining-values-and-functions)
6. [Local Binding](#local-binding)
7. [Higher-Order Functions and Closures](#higher-order-functions-and-closures)
8. [Quasiquote and Code Generation](#quasiquote-and-code-generation)
9. [Macros](#macros)
10. [Error Handling](#error-handling)
11. [Standard Library](#standard-library)
12. [Pattern Matching](#pattern-matching)
13. [Records](#records)
14. [Lazy Evaluation and Streams](#lazy-evaluation-and-streams)
15. [Advanced Standard Library](#advanced-standard-library)
16. [Multi-File Programs](#multi-file-programs)
17. [Example Programs](#example-programs)

---

## Installation and Running Code

### Installation

Install Pebble in development mode from its source directory:

```
pip install -e .
```

This installs the `pebble` console command.

### Three Ways to Run Pebble Code

**Run a file:**

```
pebble examples/fizzbuzz.pebble
```

**Start the REPL (interactive Read-Eval-Print Loop):**

```
pebble
```

Then type expressions at the `> ` prompt. Press Ctrl+D to exit.

**Evaluate a single expression:**

```
pebble -c "(+ 1 2)"
pebble -c "(map (lambda (x) (* x 2)) (list 1 2 3))"
```

---

## Data Types

Pebble has a rich set of data types, each with its own printed form.

### Integers and Floats

Numbers can be integers or floating-point:

```pebble
42 ; => 42
-17 ; => -17
3.14 ; => 3.14
0.5 ; => 0.5
```

### Strings

Strings are enclosed in double quotes. Escape sequences like `\"` and `\\` are supported:

```pebble
"hello" ; => "hello"
"multi-word string" ; => "multi-word string"
"escaped \"quotes\" and backslash \\" ; => "escaped \"quotes\" and backslash \\"
```

### Symbols

Symbols are like identifiers—they represent names or labels. You create them with the quote operator `'`:

```pebble
'x ; => x
'my-function ; => my-function
'+ ; => +
```

### Booleans and Nil

Pebble has two boolean values and an empty-list/nil value:

```pebble
true ; => true
false ; => false
nil ; => nil
```

The empty list is represented as `nil`. `nil` is both falsy (for conditionals) and an empty list.

### Lists

Lists are ordered collections enclosed in parentheses (or created with `list` and `cons`):

```pebble
(list 1 2 3) ; => (1 2 3)
(list "a" "b" "c") ; => ("a" "b" "c")
(list) ; => nil
nil ; => nil
(cons 1 nil) ; => (1)
(cons 1 (list 2 3)) ; => (1 2 3)
```

You can nest lists:

```pebble
(list 1 (list 2 3) 4) ; => (1 (2 3) 4)
```

### Hash Maps

Hash maps (dictionaries) are immutable key-value stores:

```pebble
(make-hash) ; => {}
(make-hash "name" "Alice" "age" 30) ; => {"name" "Alice", "age" 30}
```

---

## Evaluation and Quoting

### Evaluation

In Pebble, code is data. An expression is evaluated by:

1. If it's a literal (number, string, boolean), return it as-is.
2. If it's a symbol, look up its value in the current scope.
3. If it's a list `(f arg1 arg2 ...)`, evaluate `f` to get a function, evaluate each argument, and apply the function to those values.

```pebble
(+ 1 2) ; => 3
(+ 1 2 3 4) ; => 10
(* 5 6) ; => 30
(- 10 3) ; => 7
(/ 10 2) ; => 5.0
```

### Quoting

To prevent evaluation and treat an expression as literal data, use `quote` or the `'` shorthand:

```pebble
(quote (1 2 3)) ; => (1 2 3)
'(1 2 3) ; => (1 2 3)
'(+ 1 2) ; => (+ 1 2)
```

Without quoting, `(+ 1 2)` evaluates to `3`. With quoting, `'(+ 1 2)` is the unevaluated list `(+ 1 2)`.

---

## Control Flow

### The `if` Special Form

`if` evaluates a test expression, then evaluates and returns either the "then" or "else" branch:

```pebble
(if true 10 20) ; => 10
(if false 10 20) ; => 20
(if (> 5 3) "yes" "no") ; => "yes"
```

If the test is falsy (i.e., `false` or `nil`), the else branch is taken. Everything else is truthy.

```pebble
(if 0 "zero is truthy" "zero is falsy") ; => "zero is truthy"
(if nil "nil is truthy" "nil is falsy") ; => "nil is falsy"
(if false "false is truthy" "false is falsy") ; => "false is falsy"
```

### The `begin` Special Form

`begin` evaluates a sequence of expressions and returns the value of the last one:

```pebble
(begin 1 2 3) ; => 3
(begin (+ 1 2) (* 3 4) (- 5 1)) ; => 4
```

---

## Defining Values and Functions

### Defining Values

`define` binds a name to a value at the top level:

```pebble
(define x 42)
x ; => 42
(define y (+ 10 20))
y ; => 30
```

### Defining Functions

You can define a function using `define` with a function-definition shorthand. The first element of the list is the function name and parameter list, and the remaining elements are the body:

```pebble
(define (add a b) (+ a b))
(add 3 4) ; => 7
(define (square x) (* x x))
(square 5) ; => 25
```

This is syntactic sugar for:

```pebble
(define add (lambda (a b) (+ a b)))
```

Functions can have multiple body forms; the value of the last form is returned:

```pebble
(define (describe-number n)
  (define squared (* n n))
  (string-append "n=" (number->string n) ", n²=" (number->string squared)))
(describe-number 5) ; => "n=5, n²=25"
```

### Recursion

A defined function can call itself recursively:

```pebble
(define (factorial n)
  (if (= n 0)
    1
    (* n (factorial (- n 1)))))
(factorial 5) ; => 120
```

Pebble implements **tail-call optimization**, so tail-recursive functions run in constant stack space:

```pebble
(define (factorial-tail n acc)
  (if (= n 0)
    acc
    (factorial-tail (- n 1) (* n acc))))
(factorial-tail 5 1) ; => 120
```

### Mutation with `set!`

You can update an existing variable with `set!`:

```pebble
(define counter 0)
(set! counter 10)
counter ; => 10
```

---

## Local Binding

### The `let` Special Form

`let` creates local variable bindings:

```pebble
(let ((x 5) (y 10)) (+ x y)) ; => 15
(let ((name "Alice") (age 30))
  (string-append name " is " (number->string age) " years old"))
; => "Alice is 30 years old"
```

Each binding is evaluated in the *current* environment before entering the new scope, so bindings cannot reference each other. If you try `(let ((x 5) (y x)) y)`, you'll get an "undefined symbol: x" error because `x` hasn't been bound yet when `y`'s initial value is evaluated.

### The `let*` Special Form

`let*` is like `let`, but each binding can reference *previous* bindings:

```pebble
(let* ((x 5) (y (+ x 10)))
  y) ; => 15
```

### The `letrec` Special Form

`letrec` creates bindings that can refer to *themselves* and each other, enabling mutual recursion:

```pebble
(letrec ((even? (lambda (n) (if (= n 0) true (odd? (- n 1)))))
         (odd?  (lambda (n) (if (= n 0) false (even? (- n 1))))))
  (even? 4)) ; => true
```

### Named `let` (Loop Form)

Named `let` is a convenient way to write tail-recursive loops. The name becomes a function that calls itself with new arguments:

```pebble
(let loop ((i 0) (acc 0))
  (if (= i 5)
    acc
    (loop (+ i 1) (+ acc i))))
; => 10
```

This sums the numbers from 0 to 4 (0 + 1 + 2 + 3 + 4 = 10). The variable `loop` is bound to a function that takes two parameters (`i` and `acc`), and the body runs with initial values `i = 0` and `acc = 0`. Each call to `loop` with new arguments is tail-call optimized.

Another example computing factorial:

```pebble
(let fact ((n 5) (acc 1))
  (if (= n 0)
    acc
    (fact (- n 1) (* n acc))))
; => 120
```

---

## Higher-Order Functions and Closures

### Lambda and Closures

`lambda` creates an anonymous function that captures variables from its enclosing scope (a closure):

```pebble
(lambda (x) (+ x 1)) ; => <procedure (x)>
(define add-five (lambda (x) (+ x 5)))
(add-five 10) ; => 15
```

A closure remembers the environment in which it was created:

```pebble
(define (make-adder n)
  (lambda (x) (+ x n)))
(define add-ten (make-adder 10))
(add-ten 5) ; => 15
(define add-three (make-adder 3))
(add-three 7) ; => 10
```

### Variadic Functions

Both `lambda` and `define` support variadic parameters. A bare symbol collects all arguments:

```pebble
(define (sum-all . ns)
  (foldl + 0 ns))
(sum-all 1 2 3 4) ; => 10
```

Or use dotted rest syntax for fixed parameters plus a rest list:

```pebble
(define (cons-with-prefix prefix . rest)
  (cons prefix rest))
(cons-with-prefix "x" 1 2 3) ; => ("x" 1 2 3)
```

### Higher-Order Functions

Pebble's standard library includes functions that take functions as arguments:

**`map`** applies a function to each element:

```pebble
(map (lambda (x) (* x 2)) (list 1 2 3 4)) ; => (2 4 6 8)
```

**`filter`** keeps elements that satisfy a predicate:

```pebble
(filter (lambda (x) (> x 2)) (list 1 2 3 4)) ; => (3 4)
```

**`foldl`** (fold-left) accumulates a value over a list:

```pebble
(foldl + 0 (list 1 2 3 4)) ; => 10
(foldl (lambda (acc x) (cons x acc)) nil (list 1 2 3)) ; => (3 2 1)
```

---

## Quasiquote and Code Generation

Quasiquote (backtick) is like quote, but allows selective unquoting:

```pebble
`(+ 1 2) ; => (+ 1 2)
`(+ 1 ,2) ; => (+ 1 2)
```

### Unquote with `,`

`,` (unquote) evaluates an expression within a quasiquote:

```pebble
(define x 10)
`(+ 1 x) ; => (+ 1 x)
`(+ 1 ,x) ; => (+ 1 10)
```

### Unquote-Splicing with `,@`

`,@` (unquote-splicing) inserts the elements of a list:

```pebble
(define numbers (list 2 3 4))
`(1 ,@numbers 5) ; => (1 2 3 4 5)
`(1 ,(list 2 3) 4) ; => (1 (2 3) 4)
```

These features are especially useful in macros for generating code.

---

## Macros

Macros are functions that transform code at evaluation time. They operate on unevaluated arguments and return code to be evaluated.

### Defining Macros with `define-macro`

You can define a macro with a function-style shorthand (like `define`):

```pebble
(define-macro (unless test body)
  `(if ,test nil ,body))
```

Or using value-style with an explicit lambda:

```pebble
(define-macro times-two
  (lambda (x) `(* ,x 2)))
```

### Example: A Simple Macro

Here's a macro that repeats an expression a fixed number of times:

```pebble
(define-macro (repeat-expr n expr)
  `(begin ,@(repeat expr n)))
```

When you call `(repeat-expr 3 (print "hello"))`, it expands to:

```
(begin (print "hello") (print "hello") (print "hello"))
```

### Avoiding Variable Capture with `gensym`

When writing macros, you may want to use helper variables that don't accidentally shadow user variables. Use `gensym` to generate unique symbol names:

```pebble
(define-macro (my-when test body)
  (let ((temp (gensym "temp")))
    `(let ((,temp ,test))
       (if ,temp ,body nil))))
```

`gensym` creates a fresh symbol each time it's called, with unique numerical suffixes:

```pebble
(symbol? (gensym)) ; => true
(symbol? (gensym "var")) ; => true
```

Each call returns a different symbol with a unique numeric suffix (e.g., `g__gensym__1`, `var__gensym__2`, etc.).

### Standard Macros

The standard library includes many useful macros (see [Standard Library](#standard-library)).

---

## Error Handling

### The `try`/`catch` Special Form

`try` evaluates a protected expression. If it raises an error, the `catch` handler is evaluated:

```pebble
(try (+ 1 2) (catch e e)) ; => 3
(try (error "oops") (catch e e)) ; => "oops"
```

The error message (a string) is bound to the variable in the catch clause:

```pebble
(try (/ 1 0) (catch err (string-append "Error: " err)))
; => "Error: division by zero"
```

Multiple forms in the handler are evaluated in sequence, with the last form's value returned:

```pebble
(try (error "problem")
  (catch e
    (display "An error occurred: ")
    (displayln e)
    "recovered"))
; (prints "An error occurred: problem")
; => "recovered"
```

---

## Standard Library

The standard library is automatically loaded and provides a wealth of functions and macros.

### Conditional Macros

**`when`** evaluates its body only if the test is truthy:

```pebble
(when true (+ 1 2)) ; => 3
(when false (+ 1 2)) ; => nil
```

**`unless`** is the opposite—it evaluates the body only if the test is falsy:

```pebble
(unless false (+ 1 2)) ; => 3
(unless true (+ 1 2)) ; => nil
```

### Logical Operators

**`and`** returns true only if all arguments are truthy (short-circuits):

```pebble
(and true true true) ; => true
(and true false true) ; => false
```

**`or`** returns true if any argument is truthy (short-circuits):

```pebble
(or false false true) ; => true
(or false false false) ; => false
```

### Multi-Way Conditionals

**`cond`** is a multi-branch conditional:

```pebble
(cond
  ((= 1 2) "one equals two")
  ((= 2 2) "two equals two")
  (else "otherwise"))
; => "two equals two"
```

**`case`** matches a value against literal data:

```pebble
(case 2
  ((1 2 3) "small")
  ((10 20 30) "large")
  (else "unknown"))
; => "small"
```

### Loop Constructs

**`while`** repeatedly executes a body while a condition is true:

```pebble
(let ((i 0))
  (while (< i 3)
    (displayln i)
    (set! i (+ i 1))))
; (prints 0, 1, 2)
```

**`dotimes`** loops a fixed number of times with a loop variable:

```pebble
(dotimes (i 3)
  (displayln i))
; (prints 0, 1, 2)
```

### List Accessors

Classic nested car/cdr combinations:

```pebble
(define lst (list 1 2 3 4))
(car lst) ; => 1
(cadr lst) ; => 2
(caddr lst) ; => 3
(first lst) ; => 1
(second lst) ; => 2
(third lst) ; => 3
(rest lst) ; => (2 3 4)
```

### List Functions

**`length`** returns the number of elements:

```pebble
(length (list 1 2 3)) ; => 3
```

**`append`** concatenates lists:

```pebble
(append (list 1 2) (list 3 4)) ; => (1 2 3 4)
```

**`reverse`** reverses a list:

```pebble
(reverse (list 1 2 3)) ; => (3 2 1)
```

**`range`** generates a list of integers:

```pebble
(range 5) ; => (0 1 2 3 4)
(range 2 5) ; => (2 3 4)
```

**`take`** and **`drop`** extract prefixes and suffixes:

```pebble
(take (list 1 2 3 4) 2) ; => (1 2)
(drop (list 1 2 3 4) 2) ; => (3 4)
```

**`sort`** sorts a list in ascending order:

```pebble
(sort (list 3 1 4 1 5)) ; => (1 1 3 4 5)
```

**`sort-with`** sorts using a custom predicate:

```pebble
(sort-with > (list 3 1 4 1 5)) ; => (5 4 3 1 1)
```

**`contains?`** checks membership:

```pebble
(contains? (list 1 2 3) 2) ; => true
(contains? (list 1 2 3) 5) ; => false
```

**`index-of`** finds the position of an element:

```pebble
(index-of (list 1 2 3 2) 2) ; => 1
(index-of (list 1 2 3) 5) ; => -1
```

**`sum`** and **`product`** accumulate numeric lists:

```pebble
(sum (list 1 2 3 4)) ; => 10
(product (list 1 2 3 4)) ; => 24
```

**`map2`** applies a two-argument function to two lists in parallel:

```pebble
(map2 + (list 1 2 3) (list 10 20 30)) ; => (11 22 33)
```

**`zip`** pairs up elements of two lists:

```pebble
(zip (list "a" "b" "c") (list 1 2 3)) ; => (("a" 1) ("b" 2) ("c" 3))
```

### String Functions

**`string-append`** concatenates strings:

```pebble
(string-append "hello" " " "world") ; => "hello world"
```

**`string-length`** returns the length:

```pebble
(string-length "hello") ; => 5
```

**`substring`** extracts a substring:

```pebble
(substring "hello" 1 4) ; => "ell"
```

**`string-join`** joins a list of strings with a separator:

```pebble
(string-join (list "a" "b" "c") ",") ; => "a,b,c"
```

**`string-split`** splits a string:

```pebble
(string-split "a,b,c" ",") ; => ("a" "b" "c")
```

### Type Predicates

Check the type of a value:

```pebble
(number? 42) ; => true
(string? "hello") ; => true
(symbol? 'x) ; => true
(list? (list 1 2)) ; => true
(null? nil) ; => true
(boolean? true) ; => true
(integer? 42) ; => true
(float? 3.14) ; => true
```

### Type Conversions

Convert between types:

```pebble
(number->string 42) ; => "42"
(string->number "42") ; => 42
(string->symbol "x") ; => x
(symbol->string 'x) ; => "x"
```

### Hash Map Functions

Create, access, and modify hash maps:

```pebble
(define m (make-hash "x" 1 "y" 2))
(hash-ref m "x") ; => 1
(hash-ref m "z" 0) ; => 0
(hash-has? m "x") ; => true
(hash-count m) ; => 2
(hash-keys m) ; => ("x" "y")
(hash-values m) ; => (1 2)
(hash->list m) ; => (("x" 1) ("y" 2))
(hash-set m "z" 3) ; => {"x" 1, "y" 2, "z" 3}
(hash-remove m "x") ; => {"y" 2}
```

### Association Lists

Association lists (alists) are lists of [key, value] pairs:

```pebble
(define alist (list (list "x" 1) (list "y" 2)))
(assoc "x" alist) ; => ("x" 1)
(assoc "z" alist) ; => false
```

### Function Composition

Compose functions for elegant code:

```pebble
(define double (lambda (x) (* x 2)))
(define inc (lambda (x) (+ x 1)))
(define inc-then-double (compose double inc))
((compose double inc) 5) ; => 12
```

---

## Pattern Matching

### The `match` Macro

`match` is a powerful macro for destructuring and pattern matching. It compares a value against a series of patterns and evaluates the body of the first matching clause.

Patterns can be:
- **Literals** (numbers, strings, booleans) — match if equal
- **Symbols** — bind the value to the symbol
- **`_` wildcard** — matches any value without binding
- **`nil`** — matches the empty list
- **Quoted symbols** `'sym` — match if equal to that specific symbol
- **Lists** `(P1 P2 ... Pn)` — match lists of exact length with recursive pattern matching
- **Tail patterns** `(P1 ... Pn . REST)` — match lists of at least length n, binding remaining elements to REST

**Simple literal matching:**

```pebble
(match 42
  (42 "found it")
  (_ "not found"))
; => "found it"
```

**Variable binding:**

```pebble
(match (list 10 20 30)
  ((a b c) (+ a b c))
  (_ 0))
; => 60
```

**Wildcard for unused values:**

```pebble
(match (list 1 2 3)
  ((_ x _) x)
  (_ nil))
; => 2
```

**Tail patterns (rest binding):**

```pebble
(match (list 1 2 3 4)
  ((first . rest) (list "first" first "rest" rest))
  (_ nil))
; => ("first" 1 "rest" (2 3 4))
```

**Quoted symbol patterns (for tagged dispatch):**

```pebble
(match 'add
  ((quote add) (+ 5 3))
  ((quote sub) (- 5 3))
  ((quote mul) (* 5 3))
  (_ 0))
; => 8
```

**Nested patterns:**

```pebble
(match (list (list "x" 10) (list "y" 20))
  (((_ val1) (_ val2)) (+ val1 val2))
  (_ 0))
; => 30
```

---

## Records

### Defining and Using Record Types

`define-record` creates a new record (structured data) type with named fields. It automatically generates:
- A **constructor** `make-NAME` that creates instances
- A **predicate** `NAME?` that tests if a value is a record of that type
- **Accessors** `NAME-FIELD` (read-only) for each field
- **Mutators** `set-NAME-FIELD!` to update fields (records are mutable)

**Creating a record type:**

```pebble
(define-record point (x y))
```

This defines:
- `(make-point x y)` — constructor
- `(point? v)` — type predicate
- `(point-x p)` — accessor for x
- `(point-y p)` — accessor for y
- `(set-point-x! p v)` — mutator for x
- `(set-point-y! p v)` — mutator for y

**Constructing and accessing:**

```pebble
(define-record point (x y))
(define p (make-point 3 4))
(point-x p) ; => 3
(point-y p) ; => 4
```

**Type checking:**

```pebble
(define-record point (x y))
(point? (make-point 1 2)) ; => true
(point? (list 1 2)) ; => false
```

**Mutable field updates:**

```pebble
(define-record person (name age))
(define alice (make-person "Alice" 30))
(set-person-age! alice 31)
(person-age alice) ; => 31
```

**Multiple records in a program:**

```pebble
(define-record point (x y))
(define-record circle (center radius))
(define c (make-circle (make-point 0 0) 5))
(point-x (circle-center c)) ; => 0
```

---

## Lazy Evaluation and Streams

### Promises with `delay` and `force`

Pebble supports **lazy evaluation** through promises. A promise defers the evaluation of an expression until explicitly forced.

**Creating a promise:**

```pebble
(define p (delay (+ 1 2)))
(promise? p) ; => true
```

**Forcing a promise:**

```pebble
(force (delay (+ 1 2))) ; => 3
(force (delay (* 5 6))) ; => 30
```

**Memoization — a promise caches its result:**

```pebble
(define counter (delay (begin (displayln "computing...") 42)))
(force counter)
; (prints "computing...")
; => 42
(force counter)
; (no output — cached result is returned)
; => 42
```

### Lazy Streams

A **stream** is a lazy, infinite sequence. Streams are built using `stream-cons` (which delays the tail) and consumed with stream accessors.

**Basic stream construction:**

```pebble
(define s (stream-cons 1 (stream-cons 2 (stream-cons 3 nil))))
(stream-car s) ; => 1
(stream-car (stream-cdr s)) ; => 2
```

**Infinite streams:**

`integers-from` generates an infinite stream of consecutive integers:

```pebble
(stream-take (integers-from 1) 5) ; => (1 2 3 4 5)
(stream-take (integers-from 10) 3) ; => (10 11 12)
```

**Stream mapping:**

```pebble
(stream-take (stream-map (lambda (x) (* x 2)) (integers-from 1)) 5)
; => (2 4 6 8 10)
```

**Stream filtering:**

```pebble
(stream-take (stream-filter (lambda (x) (> x 5)) (integers-from 1)) 3)
; => (6 7 8)
```

**Taking elements from a stream:**

```pebble
(stream-take (integers-from 0) 10)
; => (0 1 2 3 4 5 6 7 8 9)
```

---

## Advanced Standard Library

Beyond the core functions, Pebble's standard library includes many powerful utilities for functional programming, data transformation, and numeric operations.

### Sorting and Ordering

**`sort`** — sorts a list in ascending order:

```pebble
(sort (list 3 1 4 1 5)) ; => (1 1 3 4 5)
(sort (list "banana" "apple" "cherry")) ; => ("apple" "banana" "cherry")
```

**`sort-with`** — sorts with a custom predicate:

```pebble
(sort-with > (list 3 1 4 1 5)) ; => (5 4 3 1 1)
```

### List Filtering and Partitioning

**`take-while`** — takes elements while a predicate is true:

```pebble
(take-while (lambda (x) (< x 5)) (list 1 2 3 5 6 3)) ; => (1 2 3)
```

**`partition`** — splits a list into two groups based on a predicate:

```pebble
(partition (lambda (x) (> x 2)) (list 1 2 3 4)) ; => ((3 4) (1 2))
```

### Grouping and Aggregating

**`frequencies`** — counts occurrences of each element:

```pebble
(define freq (frequencies (list 1 2 2 3 3 3)))
(hash-ref freq 1) ; => 1
(hash-ref freq 2) ; => 2
(hash-ref freq 3) ; => 3
```

**`group-by`** — groups elements by a key function:

```pebble
(define groups (group-by (lambda (x) (modulo x 2)) (list 1 2 3 4 5)))
(hash-ref groups 0) ; => (2 4)
(hash-ref groups 1) ; => (1 3 5)
```

### Function Utilities

**`partial`** — creates a partially-applied function:

```pebble
(define add10 (partial + 10))
(add10 5) ; => 15
(add10 20) ; => 30
```

**`compose`** — composes two functions:

```pebble
(define double (lambda (x) (* x 2)))
(define inc (lambda (x) (+ x 1)))
(define inc-then-double (compose double inc))
(inc-then-double 5) ; => 12
```

### Number Conversion

**`number->binary`** — converts to binary string:

```pebble
(number->binary 13) ; => "1101"
(number->binary 255) ; => "11111111"
```

**`number->hex`** — converts to hexadecimal string:

```pebble
(number->hex 255) ; => "ff"
(number->hex 256) ; => "100"
```

### String Manipulation

**`string-split`** — splits a string by a separator:

```pebble
(string-split "a,b,c" ",") ; => ("a" "b" "c")
(string-split "hello world test" " ") ; => ("hello" "world" "test")
```

**`capitalize`** — uppercases the first character:

```pebble
(capitalize "hello") ; => "Hello"
(capitalize "wORLD") ; => "WORLD"
```

### Statistics

**`mean`** — arithmetic average:

```pebble
(mean (list 1 2 3 4 5)) ; => 3.0
(mean (list 10 20)) ; => 15.0
```

**`median`** — middle value (or average of two middle values):

```pebble
(median (list 1 2 3 4 5)) ; => 3
(median (list 1 2 3 4)) ; => 2.5
```

---

## Multi-File Programs

### The `load` Special Form

For larger programs, use `load` to evaluate another Pebble file:

```scheme
(load "lib.pebble")
```

The file is evaluated in the current environment, so any `define` statements in the file become immediately available:

```scheme
(define result (load "compute.pebble"))
```

---

## Example Programs

Pebble includes several example programs in the `examples/` directory:

- **`fizzbuzz.pebble`** — Classic FizzBuzz (1-15) demonstrating recursion and conditionals
- **`fibonacci.pebble`** — Computes the first 10 Fibonacci numbers using tail recursion
- **`quicksort.pebble`** — Sorts a list using the quicksort algorithm
- **`wordcount.pebble`** — Counts word frequencies using hash maps
- **`calculator.pebble`** — An arithmetic expression evaluator with operator precedence
- **`error_handling.pebble`** — Demonstrates try/catch error handling
- **`metacircular.pebble`** — A tiny Lisp interpreter written in Pebble

Run any example:

```
python -m pebble examples/fizzbuzz.pebble
```

---

## Quick Reference

### Data Types

| Type      | Example                       | Printed Form                 |
|-----------|-------------------------------|------------------------------|
| Integer   | `42`                          | `42`                         |
| Float     | `3.14`                        | `3.14`                       |
| String    | `"hello"`                     | `"hello"`                    |
| Symbol    | `'x`                          | `x`                          |
| Boolean   | `true` or `false`             | `true` or `false`            |
| Nil       | `nil` or `(list)`             | `nil`                        |
| List      | `(list 1 2 3)`                | `(1 2 3)`                    |
| Hash Map  | `(make-hash "x" 1)`           | `{"x" 1}`                    |

### Special Forms

- `quote` / `'` — quote an expression
- `quasiquote` / `` ` `` — quote with selective unquoting (`,` and `,@`)
- `if` — conditional
- `begin` — sequence of expressions
- `define` — bind a name to a value or function
- `define-macro` — define a macro
- `set!` — update a variable
- `lambda` — create an anonymous function
- `let` — local variable bindings
- `let*` — sequential variable bindings
- `letrec` — recursive variable bindings
- `try`/`catch` — error handling
- `load` — load and evaluate another file

### Arithmetic

- `+`, `-`, `*`, `/` — arithmetic
- `modulo` — remainder
- `abs` — absolute value
- `min`, `max` — minimum/maximum
- `expt` — exponentiation

### Comparison

- `=`, `<`, `>`, `<=`, `>=` — comparison

### Lists

- `list` — construct a list
- `cons` — prepend to a list
- `car` — first element
- `cdr` — rest of list
- `length` — list length
- `append` — concatenate lists
- `reverse` — reverse a list
- `member` — check membership (returns sublist or nil)

### Higher-Order Functions

- `map` — apply a function to each element
- `filter` — keep elements satisfying a predicate
- `foldl`, `foldr` — accumulate over a list
- `for-each` — apply a function to each element (side effects)
- `apply` — apply a function to a list of arguments

### Strings

- `string-append` — concatenate strings
- `string-length` — string length
- `substring` — extract substring
- `string-join` — join strings with separator
- `string-split` — split a string

### Type Predicates

- `number?`, `integer?`, `float?` — numeric types
- `string?`, `symbol?`, `boolean?` — basic types
- `list?`, `pair?`, `null?` — list types
- `procedure?` — test if callable

### Hash Maps

- `make-hash` — create a hash map
- `hash-ref` — look up a key
- `hash-set` — add/update a key
- `hash-remove` — remove a key
- `hash-has?` — check if key exists
- `hash-count` — number of key-value pairs
- `hash-keys`, `hash-values` — get collections
- `hash->list` — convert to list of pairs

### I/O

- `display` — print (no newline)
- `displayln` — print with newline
- `print` — print with spaces between arguments
- `newline` — print newline
- `error` — raise an error

### Macros

- `when`, `unless` — simple conditionals
- `and`, `or` — logical operators
- `cond` — multi-branch conditional
- `case` — pattern matching
- `while` — loop while condition is true
- `dotimes` — loop a fixed number of times
- `gensym` — generate unique symbols

---

## Conclusion

Pebble is a powerful yet simple Lisp that supports all the fundamental programming paradigms: procedural, functional, and metaprogramming. Start with the examples and the standard library, and you'll be writing elegant, expressive code in no time.

Happy coding!
