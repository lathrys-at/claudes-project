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

    def try_lookup(self, name, default=None):
        """Look up a variable, returning default if not found.

        Args:
            name: A Symbol or str to look up.
            default: The value to return if not found (None by default).

        Returns:
            The bound value, or default if not found.
        """
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.try_lookup(name, default)
        return default


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


class Macro:
    """A macro: wraps a transformer Procedure that rewrites code at expansion time."""

    def __init__(self, transformer):
        """Create a macro.

        Args:
            transformer: A Procedure that transforms unevaluated code.
        """
        self.transformer = transformer

    def __repr__(self):
        """Return a string representation of the macro."""
        return "<macro>"


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


def expand_quasi(template, env, depth):
    """Expand a quasiquote template at the given depth.

    Args:
        template: The template to expand.
        env: The Environment for unquote evaluation.
        depth: The current quasiquote nesting depth (starts at 1).

    Returns:
        The expanded template.

    Raises:
        EvalError: For invalid unquote-splicing or other errors.
    """
    if isinstance(template, PebbleList):
        # Check for (unquote ...)
        if (len(template) == 2 and isinstance(template[0], Symbol)
            and template[0] == "unquote"):
            if depth == 1:
                return seval(template[1], env)
            else:
                return PebbleList([Symbol("unquote"), expand_quasi(template[1], env, depth - 1)])

        # Check for (quasiquote ...)
        if (len(template) == 2 and isinstance(template[0], Symbol)
            and template[0] == "quasiquote"):
            return PebbleList([Symbol("quasiquote"), expand_quasi(template[1], env, depth + 1)])

        # Otherwise, expand each element
        result = []
        for elem in template:
            # Check for (unquote-splicing ...)
            if (isinstance(elem, PebbleList) and len(elem) == 2
                and isinstance(elem[0], Symbol) and elem[0] == "unquote-splicing"):
                if depth == 1:
                    spliced = seval(elem[1], env)
                    if not isinstance(spliced, PebbleList):
                        raise EvalError(f"unquote-splicing: expected a list, got {type(spliced).__name__}")
                    result.extend(spliced)
                else:
                    result.append(PebbleList([Symbol("unquote-splicing"), expand_quasi(elem[1], env, depth - 1)]))
            else:
                result.append(expand_quasi(elem, env, depth))

        return PebbleList(result)

    # Non-list: return unchanged
    return template


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

            elif head == "quasiquote":
                if len(expr) != 2:
                    raise EvalError(f"quasiquote requires exactly 1 argument, got {len(expr) - 1}")
                return expand_quasi(expr[1], env, 1)

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

            elif head == "define-macro":
                if len(expr) < 2:
                    raise EvalError(f"define-macro requires at least 1 argument, got {len(expr) - 1}")

                # Check if it's function-style (a) or value-style (b)
                if isinstance(expr[1], PebbleList):
                    # Function-style: (define-macro (name param1 param2 ...) body...)
                    params_and_name = expr[1]
                    if len(params_and_name) == 0:
                        raise EvalError("define-macro: macro name and parameters list cannot be empty")

                    macro_name = params_and_name[0]
                    if not isinstance(macro_name, Symbol):
                        raise EvalError(f"define-macro: macro name must be a symbol, got {type(macro_name).__name__}")

                    macro_params = list(params_and_name[1:])
                    # Validate all params are symbols
                    for param in macro_params:
                        if not isinstance(param, Symbol):
                            raise EvalError(f"define-macro: parameter must be a symbol, got {type(param).__name__}")

                    body = list(expr[2:])
                    transformer = Procedure(macro_params, body, env)
                    macro = Macro(transformer)
                    env.define(macro_name, macro)
                    return macro_name

                elif isinstance(expr[1], Symbol):
                    # Value-style: (define-macro name transformer-expr)
                    if len(expr) != 3:
                        raise EvalError(f"define-macro value-style requires exactly 2 arguments, got {len(expr) - 1}")

                    macro_name = expr[1]
                    transformer_expr = expr[2]
                    transformer = seval(transformer_expr, env)

                    if not isinstance(transformer, Procedure):
                        raise EvalError("define-macro: transformer must be a procedure")

                    macro = Macro(transformer)
                    env.define(macro_name, macro)
                    return macro_name

                else:
                    raise EvalError(f"define-macro: first argument must be a symbol or list, got {type(expr[1]).__name__}")

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

            # If we reach here, head is a Symbol but no special form matched
            # Check for macro expansion
            maybe_macro = env.try_lookup(head)
            if isinstance(maybe_macro, Macro):
                # Expand the macro: apply transformer to unevaluated args
                expansion = apply_proc(maybe_macro.transformer, list(expr[1:]))
                return seval(expansion, env)

        # Not a special form and not a macro (or head is not a Symbol): it's a function call
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
    # Lazy import to avoid circular dependency
    from pebble.builtins import builtin_table

    env = Environment()
    for name, fn in builtin_table(apply_proc).items():
        env.define(Symbol(name), fn)

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
