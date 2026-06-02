"""Builtin functions for the Pebble Lisp interpreter."""
import math
from pebble.types import Symbol, PebbleList, NIL, PebbleHash, PebbleVector
from pebble.evaluator import EvalError, is_truthy

# Gensym counter for generating unique symbols
_gensym_counter = 0


def builtin_table(apply_proc):
    """Return a dict mapping builtin name (str) -> Python callable.

    Args:
        apply_proc: The evaluator's apply function, used by higher-order builtins.

    Returns:
        A dict of builtin functions.
    """

    # ===== ARITHMETIC =====

    def builtin_add(*args):
        """(+ ...) -> sum of arguments (0 if none)."""
        return sum(args)

    def builtin_sub(*args):
        """(-) or (- x) or (- x y ...) -> negation or subtraction."""
        if len(args) == 0:
            raise EvalError("- requires at least 1 argument")
        if len(args) == 1:
            return -args[0]
        result = args[0]
        for arg in args[1:]:
            result -= arg
        return result

    def builtin_mul(*args):
        """(* ...) -> product of arguments (1 if none)."""
        result = 1
        for arg in args:
            result *= arg
        return result

    def builtin_div(*args):
        """(/ x y ...) -> x / y / ... Division by zero raises EvalError."""
        if len(args) == 0:
            raise EvalError("/ requires at least 1 argument")
        result = args[0]
        for arg in args[1:]:
            if arg == 0:
                raise EvalError("division by zero")
            result = result / arg
        return result

    def builtin_modulo(a, b):
        """(modulo a b) -> a % b. Raises EvalError if b == 0."""
        if b == 0:
            raise EvalError("division by zero")
        return a % b

    def builtin_quotient(a, b):
        """(quotient a b) -> integer division truncated toward zero.

        Both arguments must be integers (not booleans).
        Raises EvalError if not integers or if b == 0.
        """
        if not isinstance(a, int) or isinstance(a, bool):
            raise EvalError(f"quotient: first argument must be an integer, got {type(a).__name__}")
        if not isinstance(b, int) or isinstance(b, bool):
            raise EvalError(f"quotient: second argument must be an integer, got {type(b).__name__}")
        if b == 0:
            raise EvalError("division by zero")
        # Truncate toward zero using exact integer arithmetic.
        # Python's // operator does floor division, so we use abs() and adjust sign.
        abs_a, abs_b = abs(a), abs(b)
        q = abs_a // abs_b
        # Negate if signs differ
        if (a < 0) != (b < 0):
            q = -q
        return q

    def builtin_remainder(a, b):
        """(remainder a b) -> remainder of truncating division.

        Result: a - b * (quotient a b). Sign follows the DIVIDEND.
        Both arguments must be integers (not booleans).
        Raises EvalError if not integers or if b == 0.
        """
        if not isinstance(a, int) or isinstance(a, bool):
            raise EvalError(f"remainder: first argument must be an integer, got {type(a).__name__}")
        if not isinstance(b, int) or isinstance(b, bool):
            raise EvalError(f"remainder: second argument must be an integer, got {type(b).__name__}")
        if b == 0:
            raise EvalError("division by zero")
        # Use exact integer arithmetic: compute quotient, then remainder = a - b * q
        abs_a, abs_b = abs(a), abs(b)
        q = abs_a // abs_b
        # Negate q if signs differ
        if (a < 0) != (b < 0):
            q = -q
        return a - b * q

    def builtin_gcd(*args):
        """(gcd ...) -> greatest common divisor of integer arguments.

        All arguments must be integers (not booleans).
        (gcd) -> 0, (gcd 5) -> 5, (gcd -12 18) -> 6, (gcd 12 18 24) -> 6.
        Result is non-negative.
        """
        for arg in args:
            if not isinstance(arg, int) or isinstance(arg, bool):
                raise EvalError(f"gcd: all arguments must be integers, got {type(arg).__name__}")

        if len(args) == 0:
            return 0

        result = abs(args[0])
        for arg in args[1:]:
            result = math.gcd(result, abs(arg))
        return result

    def builtin_lcm(*args):
        """(lcm ...) -> least common multiple of integer arguments.

        All arguments must be integers (not booleans).
        (lcm) -> 1, (lcm 4 6) -> 12, (lcm 0 5) -> 0, (lcm 2 3 4) -> 12.
        Result is non-negative.
        """
        for arg in args:
            if not isinstance(arg, int) or isinstance(arg, bool):
                raise EvalError(f"lcm: all arguments must be integers, got {type(arg).__name__}")

        if len(args) == 0:
            return 1

        result = abs(args[0])
        for arg in args[1:]:
            arg_abs = abs(arg)
            if result == 0 or arg_abs == 0:
                result = 0
            else:
                result = (result * arg_abs) // math.gcd(result, arg_abs)
        return result

    def builtin_sqrt(x):
        """(sqrt x) -> square root as a float.

        Argument must be a number (int or float, not boolean).
        Negative argument raises EvalError (no complex numbers).
        Result is always a float.
        """
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise EvalError(f"sqrt: argument must be a number, got {type(x).__name__}")
        if x < 0:
            raise EvalError("sqrt: cannot take square root of negative number")
        return math.sqrt(x)

    def builtin_floor(x):
        """(floor x) -> largest integer <= x.

        Argument must be a number (int or float, not boolean).
        Result is always an integer.
        """
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise EvalError(f"floor: argument must be a number, got {type(x).__name__}")
        return math.floor(x)

    def builtin_ceiling(x):
        """(ceiling x) -> smallest integer >= x.

        Argument must be a number (int or float, not boolean).
        Result is always an integer.
        """
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise EvalError(f"ceiling: argument must be a number, got {type(x).__name__}")
        return math.ceil(x)

    def builtin_round(x):
        """(round x) -> nearest integer using round-half-to-even (banker's rounding).

        Argument must be a number (int or float, not boolean).
        Result is always an integer.
        """
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise EvalError(f"round: argument must be a number, got {type(x).__name__}")
        return round(x)

    def builtin_truncate(x):
        """(truncate x) -> integer part toward zero.

        Argument must be a number (int or float, not boolean).
        Result is always an integer.
        """
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise EvalError(f"truncate: argument must be a number, got {type(x).__name__}")
        return math.trunc(x)

    def builtin_abs(x):
        """(abs x) -> absolute value."""
        return abs(x)

    def builtin_min(*args):
        """(min x ...) -> minimum of arguments. EvalError if no arguments."""
        if len(args) == 0:
            raise EvalError("min requires at least 1 argument")
        return min(args)

    def builtin_max(*args):
        """(max x ...) -> maximum of arguments. EvalError if no arguments."""
        if len(args) == 0:
            raise EvalError("max requires at least 1 argument")
        return max(args)

    def builtin_expt(base, exp):
        """(expt base exp) -> base ** exp."""
        return base ** exp

    # ===== COMPARISON =====

    def builtin_eq(*args):
        """(= x y ...) -> True if all args equal."""
        if len(args) == 0:
            return True
        first = args[0]
        for arg in args[1:]:
            if arg != first:
                return False
        return True

    def builtin_lt(*args):
        """(< x y ...) -> True if strictly increasing."""
        for i in range(len(args) - 1):
            if not (args[i] < args[i + 1]):
                return False
        return True

    def builtin_gt(*args):
        """(> x y ...) -> True if strictly decreasing."""
        for i in range(len(args) - 1):
            if not (args[i] > args[i + 1]):
                return False
        return True

    def builtin_le(*args):
        """(<= x y ...) -> True if non-decreasing."""
        for i in range(len(args) - 1):
            if not (args[i] <= args[i + 1]):
                return False
        return True

    def builtin_ge(*args):
        """(>= x y ...) -> True if non-increasing."""
        for i in range(len(args) - 1):
            if not (args[i] >= args[i + 1]):
                return False
        return True

    # ===== BOOLEAN =====

    def builtin_not(x):
        """(not x) -> True if x is NOT truthy, else False."""
        return not is_truthy(x)

    # ===== TYPE PREDICATES =====

    def builtin_number_p(x):
        """(number? x) -> True if x is int or float (but not bool)."""
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    def builtin_integer_p(x):
        """(integer? x) -> True if x is int (but not bool)."""
        return isinstance(x, int) and not isinstance(x, bool)

    def builtin_float_p(x):
        """(float? x) -> True if x is float."""
        return isinstance(x, float)

    def builtin_string_p(x):
        """(string? x) -> True if x is str (but not Symbol)."""
        return isinstance(x, str) and not isinstance(x, Symbol)

    def builtin_symbol_p(x):
        """(symbol? x) -> True if x is a Symbol."""
        return isinstance(x, Symbol)

    def builtin_list_p(x):
        """(list? x) -> True if x is a PebbleList."""
        return isinstance(x, PebbleList)

    def builtin_pair_p(x):
        """(pair? x) -> True if x is a non-empty PebbleList."""
        return isinstance(x, PebbleList) and len(x) > 0

    def builtin_null_p(x):
        """(null? x) -> True if x is empty PebbleList."""
        return isinstance(x, PebbleList) and len(x) == 0

    def builtin_nil_p(x):
        """(nil? x) -> True if x is empty PebbleList (alias of null?)."""
        return isinstance(x, PebbleList) and len(x) == 0

    def builtin_boolean_p(x):
        """(boolean? x) -> True if x is True or False."""
        return x is True or x is False

    def builtin_procedure_p(x):
        """(procedure? x) -> True if x is callable (Procedure or builtin)."""
        from pebble.evaluator import Procedure
        return isinstance(x, Procedure) or callable(x)

    # ===== LIST OPERATIONS =====

    def builtin_list(*args):
        """(list ...) -> PebbleList of arguments."""
        return PebbleList(args)

    def builtin_cons(x, lst):
        """(cons x lst) -> new PebbleList with x prepended."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"cons: second argument must be a list, got {type(lst).__name__}")
        return PebbleList([x] + list(lst))

    def builtin_car(lst):
        """(car lst) -> first element."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"car: argument must be a list, got {type(lst).__name__}")
        if len(lst) == 0:
            raise EvalError("car: empty list has no car")
        return lst[0]

    def builtin_cdr(lst):
        """(cdr lst) -> PebbleList of rest."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"cdr: argument must be a list, got {type(lst).__name__}")
        if len(lst) == 0:
            raise EvalError("cdr: empty list has no cdr")
        return PebbleList(lst[1:])

    def builtin_length(lst):
        """(length lst) -> int length."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"length: argument must be a list, got {type(lst).__name__}")
        return len(lst)

    def builtin_append(*args):
        """(append ...) -> concatenated PebbleList."""
        if len(args) == 0:
            return NIL
        result = []
        for lst in args:
            if not isinstance(lst, PebbleList):
                raise EvalError(f"append: argument must be a list, got {type(lst).__name__}")
            result.extend(lst)
        return PebbleList(result)

    def builtin_reverse(lst):
        """(reverse lst) -> reversed PebbleList."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"reverse: argument must be a list, got {type(lst).__name__}")
        return PebbleList(reversed(list(lst)))

    def builtin_list_ref(lst, i):
        """(list-ref lst i) -> element at index i."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"list-ref: first argument must be a list, got {type(lst).__name__}")
        if not isinstance(i, int) or isinstance(i, bool):
            raise EvalError(f"list-ref: second argument must be an integer, got {type(i).__name__}")
        try:
            return lst[i]
        except IndexError:
            raise EvalError(f"list-ref: index {i} out of range for list of length {len(lst)}")

    def builtin_member(x, lst):
        """(member x lst) -> the sublist starting at first element equal to x, or nil."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"member: second argument must be a list, got {type(lst).__name__}")
        for i, elem in enumerate(lst):
            if elem == x:
                return PebbleList(lst[i:])
        return NIL

    # ===== HIGHER-ORDER FUNCTIONS =====

    def builtin_map(f, lst):
        """(map f lst) -> PebbleList of (f element) for each element."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"map: second argument must be a list, got {type(lst).__name__}")
        result = []
        for elem in lst:
            result.append(apply_proc(f, [elem]))
        return PebbleList(result)

    def builtin_filter(pred, lst):
        """(filter pred lst) -> PebbleList of elements where (pred element) is truthy."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"filter: second argument must be a list, got {type(lst).__name__}")
        result = []
        for elem in lst:
            if is_truthy(apply_proc(pred, [elem])):
                result.append(elem)
        return PebbleList(result)

    def builtin_foldl(f, init, lst):
        """(foldl f init lst) -> accumulated result, left fold."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"foldl: third argument must be a list, got {type(lst).__name__}")
        acc = init
        for elem in lst:
            acc = apply_proc(f, [acc, elem])
        return acc

    def builtin_foldr(f, init, lst):
        """(foldr f init lst) -> accumulated result, right fold."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"foldr: third argument must be a list, got {type(lst).__name__}")
        acc = init
        for elem in reversed(list(lst)):
            acc = apply_proc(f, [elem, acc])
        return acc

    def builtin_for_each(f, lst):
        """(for-each f lst) -> apply (f element) for each element, return nil."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"for-each: second argument must be a list, got {type(lst).__name__}")
        for elem in lst:
            apply_proc(f, [elem])
        return NIL

    def builtin_apply(f, args_list):
        """(apply f args-list) -> apply f to elements of args-list."""
        if not isinstance(args_list, PebbleList):
            raise EvalError(f"apply: second argument must be a list, got {type(args_list).__name__}")
        return apply_proc(f, list(args_list))

    # ===== VECTOR OPERATIONS =====

    def builtin_vector(*args):
        """(vector e1 e2 ...) -> new PebbleVector containing the elements."""
        return PebbleVector(args)

    def builtin_make_vector(*args):
        """(make-vector n) or (make-vector n fill) -> vector of length n.

        With one arg, fills with nil. With two args, fills with fill value.
        n must be a non-negative integer.
        """
        if len(args) == 1:
            n = args[0]
            fill = NIL
        elif len(args) == 2:
            n, fill = args
        else:
            raise EvalError(f"make-vector: expected 1 or 2 arguments, got {len(args)}")

        if not isinstance(n, int) or isinstance(n, bool):
            raise EvalError(f"make-vector: first argument must be an integer, got {type(n).__name__}")
        if n < 0:
            raise EvalError(f"make-vector: length must be non-negative, got {n}")

        return PebbleVector([fill] * n)

    def builtin_vector_p(x):
        """(vector? x) -> True if x is a PebbleVector, else False."""
        return isinstance(x, PebbleVector)

    def builtin_vector_ref(v, i):
        """(vector-ref v i) -> element at index i."""
        if not isinstance(v, PebbleVector):
            raise EvalError(f"vector-ref: first argument must be a vector, got {type(v).__name__}")
        if not isinstance(i, int) or isinstance(i, bool):
            raise EvalError(f"vector-ref: second argument must be an integer, got {type(i).__name__}")
        if i < 0 or i >= len(v):
            raise EvalError(f"vector-ref: index {i} out of range for vector of length {len(v)}")
        return v[i]

    def builtin_vector_set(v, i, x):
        """(vector-set! v i x) -> mutate v at index i to x, return nil."""
        if not isinstance(v, PebbleVector):
            raise EvalError(f"vector-set!: first argument must be a vector, got {type(v).__name__}")
        if not isinstance(i, int) or isinstance(i, bool):
            raise EvalError(f"vector-set!: second argument must be an integer, got {type(i).__name__}")
        if i < 0 or i >= len(v):
            raise EvalError(f"vector-set!: index {i} out of range for vector of length {len(v)}")
        v[i] = x
        return NIL

    def builtin_vector_length(v):
        """(vector-length v) -> integer length of v."""
        if not isinstance(v, PebbleVector):
            raise EvalError(f"vector-length: argument must be a vector, got {type(v).__name__}")
        return len(v)

    def builtin_vector_to_list(v):
        """(vector->list v) -> PebbleList of v's elements."""
        if not isinstance(v, PebbleVector):
            raise EvalError(f"vector->list: argument must be a vector, got {type(v).__name__}")
        return PebbleList(v._data)

    def builtin_list_to_vector(lst):
        """(list->vector lst) -> new PebbleVector from list's elements."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"list->vector: argument must be a list, got {type(lst).__name__}")
        return PebbleVector(lst)

    def builtin_vector_push(v, x):
        """(vector-push! v x) -> append x to v, return nil."""
        if not isinstance(v, PebbleVector):
            raise EvalError(f"vector-push!: first argument must be a vector, got {type(v).__name__}")
        v.append(x)
        return NIL

    # ===== STRING OPERATIONS =====

    def builtin_string_append(*args):
        """(string-append ...) -> concatenation of all string args."""
        for arg in args:
            if not isinstance(arg, str) or isinstance(arg, Symbol):
                raise EvalError(f"string-append: all arguments must be strings, got {type(arg).__name__}")
        return "".join(args)

    def builtin_string_length(s):
        """(string-length s) -> int length."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-length: argument must be a string, got {type(s).__name__}")
        return len(s)

    def builtin_substring(s, start, end):
        """(substring s start end) -> s[start:end]."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"substring: first argument must be a string, got {type(s).__name__}")
        if not isinstance(start, int) or isinstance(start, bool):
            raise EvalError(f"substring: second argument must be an integer, got {type(start).__name__}")
        if not isinstance(end, int) or isinstance(end, bool):
            raise EvalError(f"substring: third argument must be an integer, got {type(end).__name__}")
        return s[start:end]

    def builtin_string_to_symbol(s):
        """(string->symbol s) -> Symbol(s)."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string->symbol: argument must be a string, got {type(s).__name__}")
        return Symbol(s)

    def builtin_symbol_to_string(sym):
        """(symbol->string sym) -> plain str of the symbol's text."""
        if not isinstance(sym, Symbol):
            raise EvalError(f"symbol->string: argument must be a symbol, got {type(sym).__name__}")
        return str(sym)

    def builtin_number_to_string(n):
        """(number->string n) -> str(n)."""
        if not isinstance(n, (int, float)) or isinstance(n, bool):
            raise EvalError(f"number->string: argument must be a number, got {type(n).__name__}")
        return str(n)

    def builtin_string_to_number(s):
        """(string->number s) -> int or float parsed from s, or False."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string->number: argument must be a string, got {type(s).__name__}")
        try:
            if '.' in s:
                return float(s)
            else:
                return int(s)
        except ValueError:
            return False

    def builtin_string_upcase(s):
        """(string-upcase s) -> uppercase copy of s."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-upcase: argument must be a string, got {type(s).__name__}")
        return s.upper()

    def builtin_string_downcase(s):
        """(string-downcase s) -> lowercase copy of s."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-downcase: argument must be a string, got {type(s).__name__}")
        return s.lower()

    def builtin_string_contains(s, sub):
        """(string-contains? s sub) -> True if sub occurs in s, else False."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-contains?: first argument must be a string, got {type(s).__name__}")
        if not isinstance(sub, str) or isinstance(sub, Symbol):
            raise EvalError(f"string-contains?: second argument must be a string, got {type(sub).__name__}")
        return sub in s

    def builtin_string_index(s, sub):
        """(string-index s sub) -> zero-based index of first occurrence of sub, or -1."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-index: first argument must be a string, got {type(s).__name__}")
        if not isinstance(sub, str) or isinstance(sub, Symbol):
            raise EvalError(f"string-index: second argument must be a string, got {type(sub).__name__}")
        try:
            return s.index(sub)
        except ValueError:
            return -1

    def builtin_string_prefix(prefix, s):
        """(string-prefix? prefix s) -> True if s starts with prefix."""
        if not isinstance(prefix, str) or isinstance(prefix, Symbol):
            raise EvalError(f"string-prefix?: first argument must be a string, got {type(prefix).__name__}")
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-prefix?: second argument must be a string, got {type(s).__name__}")
        return s.startswith(prefix)

    def builtin_string_suffix(suffix, s):
        """(string-suffix? suffix s) -> True if s ends with suffix."""
        if not isinstance(suffix, str) or isinstance(suffix, Symbol):
            raise EvalError(f"string-suffix?: first argument must be a string, got {type(suffix).__name__}")
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-suffix?: second argument must be a string, got {type(s).__name__}")
        return s.endswith(suffix)

    def builtin_string_repeat(s, n):
        """(string-repeat s n) -> s repeated n times. n must be a non-negative integer."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-repeat: first argument must be a string, got {type(s).__name__}")
        if not isinstance(n, int) or isinstance(n, bool):
            raise EvalError(f"string-repeat: second argument must be an integer, got {type(n).__name__}")
        if n < 0:
            raise EvalError(f"string-repeat: count must be non-negative, got {n}")
        return s * n

    def builtin_string_replace(s, old, new):
        """(string-replace s old new) -> copy of s with old replaced by new.

        old must be a non-empty string; new may be any string.
        """
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-replace: first argument must be a string, got {type(s).__name__}")
        if not isinstance(old, str) or isinstance(old, Symbol):
            raise EvalError(f"string-replace: second argument must be a string, got {type(old).__name__}")
        if not isinstance(new, str) or isinstance(new, Symbol):
            raise EvalError(f"string-replace: third argument must be a string, got {type(new).__name__}")
        if len(old) == 0:
            raise EvalError("string-replace: old string must be non-empty")
        return s.replace(old, new)

    def builtin_string_trim(s):
        """(string-trim s) -> s with leading and trailing whitespace removed."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string-trim: argument must be a string, got {type(s).__name__}")
        return s.strip()

    def builtin_char_at(s, i):
        """(char-at s i) -> one-character string at index i."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"char-at: first argument must be a string, got {type(s).__name__}")
        if not isinstance(i, int) or isinstance(i, bool):
            raise EvalError(f"char-at: second argument must be an integer, got {type(i).__name__}")
        if i < 0 or i >= len(s):
            raise EvalError(f"char-at: index {i} out of range for string of length {len(s)}")
        return s[i]

    def builtin_string_to_list(s):
        """(string->list s) -> PebbleList of one-character strings."""
        if not isinstance(s, str) or isinstance(s, Symbol):
            raise EvalError(f"string->list: argument must be a string, got {type(s).__name__}")
        return PebbleList(list(s))

    def builtin_list_to_string(lst):
        """(list->string lst) -> concatenation of strings in the list."""
        if not isinstance(lst, PebbleList):
            raise EvalError(f"list->string: argument must be a list, got {type(lst).__name__}")
        for elem in lst:
            if not isinstance(elem, str) or isinstance(elem, Symbol):
                raise EvalError(f"list->string: all elements must be strings, got {type(elem).__name__}")
        return "".join(lst)

    # ===== IO =====

    def builtin_print(*args):
        """(print ...) -> print args space-separated, return nil."""
        from pebble.printer import pebble_str
        parts = [pebble_str(arg) for arg in args]
        print(" ".join(parts))
        return NIL

    def builtin_display(*args):
        """(display ...) -> print args space-separated (no newline), return nil."""
        from pebble.printer import pebble_str
        parts = [pebble_str(arg) for arg in args]
        print(" ".join(parts), end="")
        return NIL

    def builtin_newline():
        """(newline) -> print a newline, return nil."""
        print()
        return NIL

    def builtin_error(msg):
        """(error msg) -> raise EvalError(str(msg))."""
        raise EvalError(str(msg))

    # ===== MACRO SUPPORT =====

    def builtin_gensym(*args):
        """(gensym) or (gensym prefix) -> fresh unique Symbol."""
        global _gensym_counter
        if len(args) == 0:
            prefix = "g"
        elif len(args) == 1:
            prefix_arg = args[0]
            if isinstance(prefix_arg, Symbol):
                prefix = str(prefix_arg)
            elif isinstance(prefix_arg, str):
                prefix = prefix_arg
            else:
                raise EvalError(f"gensym: prefix must be a string or symbol, got {type(prefix_arg).__name__}")
        else:
            raise EvalError(f"gensym: takes 0 or 1 argument, got {len(args)}")

        _gensym_counter += 1
        return Symbol(f"{prefix}__gensym__{_gensym_counter}")

    def builtin_macro_p(x):
        """(macro? x) -> True if x is a Macro, else False."""
        from pebble.evaluator import Macro
        return isinstance(x, Macro)

    # ===== HASH MAP OPERATIONS =====

    def builtin_make_hash(*args):
        """(make-hash) or (make-hash k1 v1 k2 v2 ...) -> PebbleHash.

        Creates an empty hash map if no args, or builds one from alternating
        key/value arguments. Raises EvalError if odd number of arguments.
        """
        if len(args) % 2 != 0:
            raise EvalError(f"make-hash: expected even number of arguments, got {len(args)}")

        data = {}
        for i in range(0, len(args), 2):
            key = args[i]
            value = args[i + 1]
            # Try to use the key; if unhashable, raise EvalError
            try:
                data[key] = value
            except TypeError as e:
                raise EvalError(f"make-hash: unhashable key type {type(key).__name__}")

        return PebbleHash(data)

    def builtin_hash_p(x):
        """(hash? x) -> True if x is a PebbleHash, else False."""
        return isinstance(x, PebbleHash)

    def builtin_hash_set(m, k, v):
        """(hash-set m k v) -> new PebbleHash with k mapped to v.

        Returns a new hash map with the same entries as m plus/replacing k->v.
        m is unchanged. Raises EvalError if m is not a hash map or key is unhashable.
        """
        if not isinstance(m, PebbleHash):
            raise EvalError(f"hash-set: first argument must be a hash map, got {type(m).__name__}")

        try:
            new_data = dict(m._data)
            new_data[k] = v
        except TypeError as e:
            raise EvalError(f"hash-set: unhashable key type {type(k).__name__}")

        return PebbleHash(new_data)

    def builtin_hash_ref(m, k, *args):
        """(hash-ref m k) or (hash-ref m k default) -> value at key k.

        If k is present in m, returns its value. If absent and no default given,
        raises EvalError. If absent and default given, returns default.
        Raises EvalError if m is not a hash map.
        """
        if not isinstance(m, PebbleHash):
            raise EvalError(f"hash-ref: first argument must be a hash map, got {type(m).__name__}")

        if len(args) == 0:
            # No default: must have key
            if k in m:
                return m.get(k)
            else:
                raise EvalError(f"hash-ref: key not found in hash map")
        elif len(args) == 1:
            # With default
            default = args[0]
            return m.get(k, default)
        else:
            raise EvalError(f"hash-ref: expected 2 or 3 arguments, got {2 + len(args)}")

    def builtin_hash_has_p(m, k):
        """(hash-has? m k) -> True if k is a key in m, else False.

        Raises EvalError if m is not a hash map.
        """
        if not isinstance(m, PebbleHash):
            raise EvalError(f"hash-has?: first argument must be a hash map, got {type(m).__name__}")
        return k in m

    def builtin_hash_remove(m, k):
        """(hash-remove m k) -> new hash map with key k removed.

        If k is absent, returns a map equal to m (no error).
        m is unchanged. Raises EvalError if m is not a hash map.
        """
        if not isinstance(m, PebbleHash):
            raise EvalError(f"hash-remove: first argument must be a hash map, got {type(m).__name__}")

        new_data = dict(m._data)
        new_data.pop(k, None)  # Remove if present, no-op if absent
        return PebbleHash(new_data)

    def builtin_hash_count(m):
        """(hash-count m) -> integer number of key/value pairs in m.

        Raises EvalError if m is not a hash map.
        """
        if not isinstance(m, PebbleHash):
            raise EvalError(f"hash-count: argument must be a hash map, got {type(m).__name__}")
        return len(m)

    def builtin_hash_keys(m):
        """(hash-keys m) -> PebbleList of keys in m.

        Raises EvalError if m is not a hash map.
        """
        if not isinstance(m, PebbleHash):
            raise EvalError(f"hash-keys: argument must be a hash map, got {type(m).__name__}")
        return PebbleList(m.keys())

    def builtin_hash_values(m):
        """(hash-values m) -> PebbleList of values in m.

        Raises EvalError if m is not a hash map.
        """
        if not isinstance(m, PebbleHash):
            raise EvalError(f"hash-values: argument must be a hash map, got {type(m).__name__}")
        return PebbleList(m.values())

    def builtin_hash_to_list(m):
        """(hash->list m) -> PebbleList of [key value] pairs.

        Returns a list of two-element lists, one for each key/value pair.
        Raises EvalError if m is not a hash map.
        """
        if not isinstance(m, PebbleHash):
            raise EvalError(f"hash->list: argument must be a hash map, got {type(m).__name__}")

        result = []
        for key, value in m.items():
            result.append(PebbleList([key, value]))
        return PebbleList(result)

    # ===== BUILD AND RETURN BUILTIN TABLE =====

    return {
        "+": builtin_add,
        "-": builtin_sub,
        "*": builtin_mul,
        "/": builtin_div,
        "modulo": builtin_modulo,
        "quotient": builtin_quotient,
        "remainder": builtin_remainder,
        "gcd": builtin_gcd,
        "lcm": builtin_lcm,
        "sqrt": builtin_sqrt,
        "floor": builtin_floor,
        "ceiling": builtin_ceiling,
        "round": builtin_round,
        "truncate": builtin_truncate,
        "abs": builtin_abs,
        "min": builtin_min,
        "max": builtin_max,
        "expt": builtin_expt,
        "=": builtin_eq,
        "<": builtin_lt,
        ">": builtin_gt,
        "<=": builtin_le,
        ">=": builtin_ge,
        "not": builtin_not,
        "number?": builtin_number_p,
        "integer?": builtin_integer_p,
        "float?": builtin_float_p,
        "string?": builtin_string_p,
        "symbol?": builtin_symbol_p,
        "list?": builtin_list_p,
        "pair?": builtin_pair_p,
        "null?": builtin_null_p,
        "nil?": builtin_nil_p,
        "boolean?": builtin_boolean_p,
        "procedure?": builtin_procedure_p,
        "list": builtin_list,
        "cons": builtin_cons,
        "car": builtin_car,
        "cdr": builtin_cdr,
        "length": builtin_length,
        "append": builtin_append,
        "reverse": builtin_reverse,
        "list-ref": builtin_list_ref,
        "member": builtin_member,
        "map": builtin_map,
        "filter": builtin_filter,
        "foldl": builtin_foldl,
        "foldr": builtin_foldr,
        "for-each": builtin_for_each,
        "apply": builtin_apply,
        "vector": builtin_vector,
        "make-vector": builtin_make_vector,
        "vector?": builtin_vector_p,
        "vector-ref": builtin_vector_ref,
        "vector-set!": builtin_vector_set,
        "vector-length": builtin_vector_length,
        "vector->list": builtin_vector_to_list,
        "list->vector": builtin_list_to_vector,
        "vector-push!": builtin_vector_push,
        "string-append": builtin_string_append,
        "string-length": builtin_string_length,
        "substring": builtin_substring,
        "string->symbol": builtin_string_to_symbol,
        "symbol->string": builtin_symbol_to_string,
        "number->string": builtin_number_to_string,
        "string->number": builtin_string_to_number,
        "string-upcase": builtin_string_upcase,
        "string-downcase": builtin_string_downcase,
        "string-contains?": builtin_string_contains,
        "string-index": builtin_string_index,
        "string-prefix?": builtin_string_prefix,
        "string-suffix?": builtin_string_suffix,
        "string-repeat": builtin_string_repeat,
        "string-replace": builtin_string_replace,
        "string-trim": builtin_string_trim,
        "char-at": builtin_char_at,
        "string->list": builtin_string_to_list,
        "list->string": builtin_list_to_string,
        "print": builtin_print,
        "display": builtin_display,
        "newline": builtin_newline,
        "error": builtin_error,
        "gensym": builtin_gensym,
        "macro?": builtin_macro_p,
        "make-hash": builtin_make_hash,
        "hash?": builtin_hash_p,
        "hash-set": builtin_hash_set,
        "hash-ref": builtin_hash_ref,
        "hash-has?": builtin_hash_has_p,
        "hash-remove": builtin_hash_remove,
        "hash-count": builtin_hash_count,
        "hash-keys": builtin_hash_keys,
        "hash-values": builtin_hash_values,
        "hash->list": builtin_hash_to_list,
    }
