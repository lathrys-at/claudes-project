"""Evaluator for Pebble Lisp."""
from pebble.types import Symbol, PebbleList, NIL
from pebble.reader import read


class EvalError(Exception):
    """Raised when there is an error evaluating Pebble code."""
    pass


class Environment:
    """A lexical scope for variable bindings."""

    def __init__(self, parent=None):
        """Create an environment with an optional parent.

        Args:
            parent: The parent Environment (for lexical scoping), or None for global.
        """
        self.vars = {}
        self.parent = parent

    def define(self, name, value):
        """Define a variable in THIS environment (not parent scopes).

        Args:
            name: A Symbol or str to define.
            value: The value to bind.
        """
        self.vars[name] = value

    def lookup(self, name):
        """Look up a variable, searching this env then parents.

        Args:
            name: A Symbol or str to look up.

        Returns:
            The bound value.

        Raises:
            EvalError: If the name is not found.
        """
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise EvalError(f"undefined symbol: {name}")

    def set(self, name, value):
        """Update a variable in the nearest scope where it's defined.

        Args:
            name: A Symbol or str to update.
            value: The new value.

        Raises:
            EvalError: If the name is not defined in this or any parent scope.
        """
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent is not None:
            self.parent.set(name, value)
            return
        raise EvalError(f"cannot set undefined symbol: {name}")


class Procedure:
    """A Pebble closure (lambda function)."""

    def __init__(self, params, body, env):
        """Create a procedure.

        Args:
            params: List of Symbols (the formal parameters).
            body: List of forms to evaluate in the body.
            env: The Environment where this procedure was defined (closure).
        """
        self.params = params
        self.body = body
        self.env = env

    def __repr__(self):
        """Return a string representation of the procedure."""
        param_names = " ".join(str(p) for p in self.params)
        return f"<procedure ({param_names})>"


def is_truthy(value) -> bool:
    """Determine if a value is truthy in Pebble.

    Returns:
        False if value is False (using 'is' to avoid 0 == False gotcha) or empty PebbleList.
        True otherwise (including 0, 0.0, and "").
    """
    if value is False:
        return False
    if isinstance(value, PebbleList) and len(value) == 0:
        return False
    return True


def seval(expr, env):
    """Evaluate a Pebble expression.

    Args:
        expr: A Pebble value to evaluate.
        env: The Environment in which to evaluate it.

    Returns:
        The result of evaluation.

    Raises:
        EvalError: For various evaluation errors.
    """
    # Symbol: look it up
    if isinstance(expr, Symbol):
        return env.lookup(expr)

    # PebbleList: either a special form or a function call
    if isinstance(expr, PebbleList):
        # Empty list is self-evaluating (NIL)
        if len(expr) == 0:
            return expr

        # Check for special forms
        head = expr[0]
        if isinstance(head, Symbol):
            if head == "quote":
                if len(expr) != 2:
                    raise EvalError(f"quote requires exactly 1 argument, got {len(expr) - 1}")
                return expr[1]

            elif head == "if":
                if len(expr) < 3 or len(expr) > 4:
                    raise EvalError(f"if requires 2 or 3 arguments, got {len(expr) - 1}")
                test_val = seval(expr[1], env)
                if is_truthy(test_val):
                    return seval(expr[2], env)
                else:
                    if len(expr) == 4:
                        return seval(expr[3], env)
                    else:
                        return NIL

            elif head == "define":
                if len(expr) != 3:
                    raise EvalError(f"define requires exactly 2 arguments, got {len(expr) - 1}")
                name = expr[1]
                if not isinstance(name, Symbol):
                    raise EvalError(f"define: first argument must be a symbol, got {type(name).__name__}")
                value = seval(expr[2], env)
                env.define(name, value)
                return name

            elif head == "set!":
                if len(expr) != 3:
                    raise EvalError(f"set! requires exactly 2 arguments, got {len(expr) - 1}")
                name = expr[1]
                if not isinstance(name, Symbol):
                    raise EvalError(f"set!: first argument must be a symbol, got {type(name).__name__}")
                value = seval(expr[2], env)
                env.set(name, value)
                return value

            elif head == "lambda":
                if len(expr) < 2:
                    raise EvalError(f"lambda requires at least 1 argument (params list), got {len(expr) - 1}")
                params_list = expr[1]
                if not isinstance(params_list, PebbleList):
                    raise EvalError(f"lambda: parameter list must be a list, got {type(params_list).__name__}")
                # Validate that all params are symbols
                for param in params_list:
                    if not isinstance(param, Symbol):
                        raise EvalError(f"lambda: parameter must be a symbol, got {type(param).__name__}")
                body = list(expr[2:])
                return Procedure(list(params_list), body, env)

            elif head == "let":
                if len(expr) < 2:
                    raise EvalError(f"let requires at least 1 argument (bindings list), got {len(expr) - 1}")
                bindings = expr[1]
                if not isinstance(bindings, PebbleList):
                    raise EvalError(f"let: bindings must be a list, got {type(bindings).__name__}")
                # Evaluate each binding in the current env
                binding_dict = {}
                for binding in bindings:
                    if not isinstance(binding, PebbleList) or len(binding) != 2:
                        raise EvalError(f"let: each binding must be a [name value] pair")
                    name, value_expr = binding[0], binding[1]
                    if not isinstance(name, Symbol):
                        raise EvalError(f"let: binding name must be a symbol, got {type(name).__name__}")
                    binding_dict[name] = seval(value_expr, env)

                # Create new env, define the bindings, evaluate body
                new_env = Environment(parent=env)
                for name, value in binding_dict.items():
                    new_env.define(name, value)

                body = expr[2:]
                if len(body) == 0:
                    return NIL
                result = NIL
                for form in body:
                    result = seval(form, new_env)
                return result

            elif head == "begin":
                body = expr[1:]
                if len(body) == 0:
                    return NIL
                result = NIL
                for form in body:
                    result = seval(form, env)
                return result

        # Not a special form: it's a function call
        # Evaluate the head and all arguments
        proc = seval(head, env)
        args = [seval(arg, env) for arg in expr[1:]]
        return apply_proc(proc, args)

    # Self-evaluating: numbers, strings, booleans, etc.
    return expr


def apply_proc(proc, args):
    """Apply a procedure to arguments.

    Args:
        proc: A Procedure or a callable (builtin).
        args: A list of evaluated arguments.

    Returns:
        The result of the function call.

    Raises:
        EvalError: If proc is not callable or arity mismatches.
    """
    if isinstance(proc, Procedure):
        # Check arity
        if len(args) != len(proc.params):
            raise EvalError(f"expected {len(proc.params)} arguments, got {len(args)}")

        # Create new env with bindings
        call_env = Environment(parent=proc.env)
        for param, arg in zip(proc.params, args):
            call_env.define(param, arg)

        # Evaluate body
        if len(proc.body) == 0:
            return NIL
        result = NIL
        for form in proc.body:
            result = seval(form, call_env)
        return result

    elif callable(proc):
        # It's a Python function (builtin)
        return proc(*args)

    else:
        raise EvalError(f"not callable: {proc}")


def make_global_env() -> Environment:
    """Create the global environment with primitive builtins.

    Returns:
        An Environment with starter builtins defined.
    """
    env = Environment()

    # Arithmetic
    def builtin_add(*args):
        return sum(args)

    def builtin_sub(*args):
        if len(args) == 0:
            return 0
        if len(args) == 1:
            return -args[0]
        result = args[0]
        for arg in args[1:]:
            result -= arg
        return result

    def builtin_mul(*args):
        result = 1
        for arg in args:
            result *= arg
        return result

    def builtin_div(*args):
        if len(args) == 0:
            raise EvalError("/ requires at least 1 argument")
        result = args[0]
        for arg in args[1:]:
            if arg == 0:
                raise EvalError("division by zero")
            result = result / arg
        return result

    # Comparison
    def builtin_eq(*args):
        if len(args) == 0:
            return True
        first = args[0]
        for arg in args[1:]:
            if arg != first:
                return False
        return True

    def builtin_lt(*args):
        for i in range(len(args) - 1):
            if not (args[i] < args[i + 1]):
                return False
        return True

    def builtin_gt(*args):
        for i in range(len(args) - 1):
            if not (args[i] > args[i + 1]):
                return False
        return True

    def builtin_le(*args):
        for i in range(len(args) - 1):
            if not (args[i] <= args[i + 1]):
                return False
        return True

    def builtin_ge(*args):
        for i in range(len(args) - 1):
            if not (args[i] >= args[i + 1]):
                return False
        return True

    # List operations
    def builtin_list(*args):
        return PebbleList(args)

    def builtin_cons(x, lst):
        if not isinstance(lst, PebbleList):
            raise EvalError(f"cons: second argument must be a list, got {type(lst).__name__}")
        return PebbleList([x] + list(lst))

    def builtin_car(lst):
        if not isinstance(lst, PebbleList):
            raise EvalError(f"car: argument must be a list, got {type(lst).__name__}")
        if len(lst) == 0:
            raise EvalError("car: empty list has no car")
        return lst[0]

    def builtin_cdr(lst):
        if not isinstance(lst, PebbleList):
            raise EvalError(f"cdr: argument must be a list, got {type(lst).__name__}")
        if len(lst) == 0:
            raise EvalError("cdr: empty list has no cdr")
        return PebbleList(lst[1:])

    def builtin_null(lst):
        if isinstance(lst, PebbleList) and len(lst) == 0:
            return True
        return False

    def builtin_print(*args):
        print(" ".join(str(arg) for arg in args))
        return NIL

    # Register all builtins
    env.define(Symbol("+"), builtin_add)
    env.define(Symbol("-"), builtin_sub)
    env.define(Symbol("*"), builtin_mul)
    env.define(Symbol("/"), builtin_div)
    env.define(Symbol("="), builtin_eq)
    env.define(Symbol("<"), builtin_lt)
    env.define(Symbol(">"), builtin_gt)
    env.define(Symbol("<="), builtin_le)
    env.define(Symbol(">="), builtin_ge)
    env.define(Symbol("list"), builtin_list)
    env.define(Symbol("cons"), builtin_cons)
    env.define(Symbol("car"), builtin_car)
    env.define(Symbol("cdr"), builtin_cdr)
    env.define(Symbol("null?"), builtin_null)
    env.define(Symbol("print"), builtin_print)

    return env


def eval_source(source, env):
    """Evaluate all forms in a source string.

    Args:
        source: A string of Pebble source code.
        env: The Environment in which to evaluate.

    Returns:
        The value of the last form, or NIL if empty.
    """
    forms = read(source)
    if len(forms) == 0:
        return NIL
    result = NIL
    for form in forms:
        result = seval(form, env)
    return result
