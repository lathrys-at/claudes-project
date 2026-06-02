"""Builtin functions for the Pebble Lisp interpreter."""
from pebble.types import Symbol, PebbleList, NIL
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

    # ===== BUILD AND RETURN BUILTIN TABLE =====

    return {
        "+": builtin_add,
        "-": builtin_sub,
        "*": builtin_mul,
        "/": builtin_div,
        "modulo": builtin_modulo,
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
        "string-append": builtin_string_append,
        "string-length": builtin_string_length,
        "substring": builtin_substring,
        "string->symbol": builtin_string_to_symbol,
        "symbol->string": builtin_symbol_to_string,
        "number->string": builtin_number_to_string,
        "string->number": builtin_string_to_number,
        "print": builtin_print,
        "display": builtin_display,
        "newline": builtin_newline,
        "error": builtin_error,
        "gensym": builtin_gensym,
        "macro?": builtin_macro_p,
    }
