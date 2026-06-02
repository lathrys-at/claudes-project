"""Evaluator for Pebble Lisp."""
from pebble.types import Symbol, PebbleList, NIL
from pebble.reader import read, ReadError


class EvalError(Exception):
    """Raised when there is an error evaluating Pebble code."""
    pass


# Trampoline objects for tail-call optimization
class _TailCall:
    """Represents a tail call to be evaluated."""
    __slots__ = ('expr', 'env')

    def __init__(self, expr, env):
        self.expr = expr
        self.env = env


def parse_param_spec(spec):
    """Parse a lambda/macro parameter specification.
    Returns a tuple (fixed_params, rest_param) where fixed_params is a list of
    Symbols and rest_param is a Symbol or None.
    Accepts:
      - a bare Symbol  -> ([], that_symbol)        # collects all args
      - a PebbleList of Symbols with no dot -> (list, None)
      - a PebbleList containing a single Symbol('.') as the second-to-last
        element, followed by exactly one rest Symbol -> (fixed_before_dot, rest_symbol)
    Raises EvalError on malformed specs (dot not in the second-to-last position,
    more than one dot, missing rest symbol after dot, or non-Symbol params).
    """
    # If spec is a bare Symbol, return ([], spec)
    if isinstance(spec, Symbol):
        return ([], spec)

    # If spec is a PebbleList
    if isinstance(spec, PebbleList):
        # Find indices of any element equal to Symbol(".")
        dot_indices = []
        for i, elem in enumerate(spec):
            if isinstance(elem, Symbol) and str(elem) == ".":
                dot_indices.append(i)

        # No dots: all elements must be Symbols
        if len(dot_indices) == 0:
            for param in spec:
                if not isinstance(param, Symbol):
                    raise EvalError(f"parameter must be a symbol, got {type(param).__name__}")
            return (list(spec), None)

        # Exactly one dot
        if len(dot_indices) == 1:
            dot_index = dot_indices[0]
            # Dot must be at position len(spec) - 2
            if dot_index != len(spec) - 2:
                raise EvalError("malformed rest parameter: dot must be second-to-last")
            # There must be exactly one element after the dot
            if len(spec) - dot_index != 2:
                raise EvalError("malformed rest parameter: missing rest symbol after dot")

            # All elements before the dot must be Symbols
            for param in spec[:dot_index]:
                if not isinstance(param, Symbol):
                    raise EvalError(f"parameter must be a symbol, got {type(param).__name__}")

            # The element after the dot must be a Symbol
            rest_param = spec[dot_index + 1]
            if not isinstance(rest_param, Symbol):
                raise EvalError(f"rest parameter must be a symbol, got {type(rest_param).__name__}")

            return (list(spec[:dot_index]), rest_param)

        # Two or more dots
        raise EvalError("malformed parameter list: multiple dots")

    # Not a Symbol and not a PebbleList
    raise EvalError("invalid parameter specification")


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

    def __init__(self, params, body, env, rest=None):
        """Create a procedure.

        Args:
            params: List of Symbols (the formal parameters).
            body: List of forms to evaluate in the body.
            env: The Environment where this procedure was defined (closure).
            rest: Optional Symbol for collecting remaining arguments as a PebbleList.
        """
        self.params = params
        self.body = body
        self.env = env
        self.rest = rest

    def __repr__(self):
        """Return a string representation of the procedure."""
        if self.rest is not None:
            if len(self.params) == 0:
                # Bare symbol parameter: (lambda args ...)
                return f"<procedure {self.rest}>"
            else:
                # Dotted rest: (lambda (a b . rest) ...)
                param_names = " ".join(str(p) for p in self.params)
                return f"<procedure ({param_names} . {self.rest})>"
        else:
            # No rest parameter
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


def _seval_internal(expr, env):
    """Internal evaluation function that may return _TailCall objects.

    This is the core evaluator that handles tail position detection.
    Do not call this directly from user code; use seval instead.

    Args:
        expr: A Pebble value to evaluate.
        env: The Environment in which to evaluate it.

    Returns:
        Either a final value or a _TailCall object for further evaluation.

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
                test_val = _trampoline(_seval_internal(expr[1], env))
                if is_truthy(test_val):
                    # Tail call: return it for the trampoline to execute
                    return _TailCall(expr[2], env)
                else:
                    if len(expr) == 4:
                        # Tail call: return it for the trampoline to execute
                        return _TailCall(expr[3], env)
                    else:
                        return NIL

            elif head == "define":
                if len(expr) < 2:
                    raise EvalError(f"define requires at least 1 argument, got {len(expr) - 1}")

                # Check if it's function-style (a) or value-style (b)
                if isinstance(expr[1], PebbleList):
                    # Function-style: (define (name param1 param2 ...) body...)
                    params_and_name = expr[1]
                    if len(params_and_name) == 0:
                        raise EvalError("define: function name and parameters list cannot be empty")

                    func_name = params_and_name[0]
                    if not isinstance(func_name, Symbol):
                        raise EvalError(f"define: function name must be a symbol, got {type(func_name).__name__}")

                    # Parse the parameters (everything after the name)
                    param_spec = PebbleList(params_and_name[1:])
                    fixed, rest = parse_param_spec(param_spec)

                    body = list(expr[2:])
                    procedure = Procedure(fixed, body, env, rest=rest)
                    env.define(func_name, procedure)
                    return func_name

                elif isinstance(expr[1], Symbol):
                    # Value-style: (define name value-expr)
                    if len(expr) != 3:
                        raise EvalError(f"define requires exactly 2 arguments, got {len(expr) - 1}")

                    name = expr[1]
                    # Value-style: (define name value-expr)
                    value = _trampoline(_seval_internal(expr[2], env))
                    env.define(name, value)
                    return name

                else:
                    raise EvalError(f"define: first argument must be a symbol or list, got {type(expr[1]).__name__}")

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

                    # Parse the parameters (everything after the name)
                    param_spec = PebbleList(params_and_name[1:])
                    fixed, rest = parse_param_spec(param_spec)

                    body = list(expr[2:])
                    transformer = Procedure(fixed, body, env, rest=rest)
                    macro = Macro(transformer)
                    env.define(macro_name, macro)
                    return macro_name

                elif isinstance(expr[1], Symbol):
                    # Value-style: (define-macro name transformer-expr)
                    if len(expr) != 3:
                        raise EvalError(f"define-macro value-style requires exactly 2 arguments, got {len(expr) - 1}")

                    macro_name = expr[1]
                    transformer_expr = expr[2]
                    transformer = _trampoline(_seval_internal(transformer_expr, env))

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
                value = _trampoline(_seval_internal(expr[2], env))
                env.set(name, value)
                return value

            elif head == "lambda":
                if len(expr) < 2:
                    raise EvalError(f"lambda requires at least 1 argument (params list), got {len(expr) - 1}")
                fixed, rest = parse_param_spec(expr[1])
                body = list(expr[2:])
                return Procedure(fixed, body, env, rest=rest)

            elif head == "let":
                if len(expr) < 2:
                    raise EvalError(f"let requires at least 1 argument, got {len(expr) - 1}")

                # Determine if this is a named let or ordinary let
                # Named let: (let NAME (bindings...) body...)
                # Ordinary let: (let (bindings...) body...)
                if isinstance(expr[1], Symbol):
                    # Named let form
                    loop_name = expr[1]
                    if len(expr) < 3:
                        raise EvalError(f"named let requires a bindings list, got {len(expr) - 1}")
                    bindings = expr[2]
                    body = expr[3:]

                    if not isinstance(bindings, PebbleList):
                        raise EvalError(f"let: bindings must be a list, got {type(bindings).__name__}")

                    # Parse bindings and evaluate inits in the current environment
                    var_names = []
                    init_values = []
                    for binding in bindings:
                        if not isinstance(binding, PebbleList) or len(binding) != 2:
                            raise EvalError(f"let: each binding must be a [name value] pair")
                        name, value_expr = binding[0], binding[1]
                        if not isinstance(name, Symbol):
                            raise EvalError(f"let: binding name must be a symbol, got {type(name).__name__}")
                        var_names.append(name)
                        init_values.append(_trampoline(_seval_internal(value_expr, env)))

                    # Create a new environment where we'll bind the loop name to itself
                    named_let_env = Environment(parent=env)

                    # Create a procedure with the parameter names
                    # The body of the procedure is the named let body
                    proc = Procedure(var_names, body, named_let_env, rest=None)

                    # Bind the loop name to the procedure in its own environment
                    # This allows the loop to call itself
                    named_let_env.define(loop_name, proc)

                    # Apply the procedure immediately with the evaluated init values
                    return _apply_proc_internal(proc, init_values)

                else:
                    # Ordinary let form: (let (bindings...) body...)
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
                        binding_dict[name] = _trampoline(_seval_internal(value_expr, env))

                    # Create new env, define the bindings, evaluate body
                    new_env = Environment(parent=env)
                    for name, value in binding_dict.items():
                        new_env.define(name, value)

                    body = expr[2:]
                    if len(body) == 0:
                        return NIL
                    # Process body: only the last form is in tail position
                    for form in body[:-1]:
                        _trampoline(_seval_internal(form, new_env))
                    # The last form is in tail position
                    return _TailCall(body[-1], new_env)

            elif head == "letrec":
                if len(expr) < 2:
                    raise EvalError(f"letrec requires at least 1 argument (bindings list), got {len(expr) - 1}")
                bindings = expr[1]
                if not isinstance(bindings, PebbleList):
                    raise EvalError(f"letrec: bindings must be a list, got {type(bindings).__name__}")

                # Create a new environment (child of current env)
                new_env = Environment(parent=env)

                # Parse bindings and create empty slots for all names
                binding_dict = {}
                for binding in bindings:
                    if not isinstance(binding, PebbleList) or len(binding) != 2:
                        raise EvalError(f"letrec: each binding must be a [name value] pair")
                    name, value_expr = binding[0], binding[1]
                    if not isinstance(name, Symbol):
                        raise EvalError(f"letrec: binding name must be a symbol, got {type(name).__name__}")
                    binding_dict[name] = value_expr

                # Define all names in the new environment (with placeholder values, which will be updated)
                # This allows forward references in the inits
                for name in binding_dict:
                    new_env.define(name, None)

                # Evaluate each init expression in the shared new environment and bind it
                for name, value_expr in binding_dict.items():
                    value = _trampoline(_seval_internal(value_expr, new_env))
                    new_env.define(name, value)

                # Evaluate the body in the shared environment
                body = expr[2:]
                if len(body) == 0:
                    return NIL
                # Process body: only the last form is in tail position
                for form in body[:-1]:
                    _trampoline(_seval_internal(form, new_env))
                # The last form is in tail position
                return _TailCall(body[-1], new_env)

            elif head == "begin":
                body = expr[1:]
                if len(body) == 0:
                    return NIL
                # Process body: only the last form is in tail position
                for form in body[:-1]:
                    _trampoline(_seval_internal(form, env))
                # The last form is in tail position
                return _TailCall(body[-1], env)

            elif head == "load":
                # (load PATH-EXPR)
                if len(expr) != 2:
                    raise EvalError(f"load requires exactly 1 argument, got {len(expr) - 1}")

                # Evaluate the path expression in the current environment
                path_expr = expr[1]
                path = _trampoline(_seval_internal(path_expr, env))

                # The result must be a string
                if not isinstance(path, str):
                    raise EvalError(f"load: path must be a string, got {type(path).__name__}")

                # Try to read the file
                try:
                    with open(path, 'r') as f:
                        source = f.read()
                except FileNotFoundError:
                    raise EvalError(f"load: file not found: {path}")
                except IOError as e:
                    raise EvalError(f"load: cannot read file {path}: {e}")

                # Parse the file contents
                try:
                    forms = read(source)
                except ReadError as e:
                    raise EvalError(f"load: parse error in {path}: {e}")

                # Evaluate each form in order in the current environment
                result = NIL
                for form in forms:
                    result = _trampoline(_seval_internal(form, env))

                # Return the value of the last form
                return result

            elif head == "try":
                # (try EXPR (catch NAME HANDLER...))
                if len(expr) != 3:
                    raise EvalError(f"try requires exactly 2 arguments (expr and catch clause), got {len(expr) - 1}")

                protected_expr = expr[1]
                catch_clause = expr[2]

                # Validate catch clause structure
                if not isinstance(catch_clause, PebbleList):
                    raise EvalError(f"catch clause must be a list, got {type(catch_clause).__name__}")
                if len(catch_clause) < 1:
                    raise EvalError("catch clause cannot be empty")
                if not isinstance(catch_clause[0], Symbol) or catch_clause[0] != "catch":
                    raise EvalError("catch clause must start with 'catch'")
                if len(catch_clause) < 2:
                    raise EvalError("catch clause must have a variable name")

                error_var = catch_clause[1]
                if not isinstance(error_var, Symbol):
                    raise EvalError(f"catch variable must be a symbol, got {type(error_var).__name__}")

                handler_forms = list(catch_clause[2:])

                # Try to evaluate the protected expression
                try:
                    # Evaluate the protected expression and trampoline the result
                    protected_result = _seval_internal(protected_expr, env)
                    return _trampoline(protected_result)
                except EvalError as e:
                    # Create a new scope for the handler
                    handler_env = Environment(parent=env)
                    # Bind the error message to the error variable
                    handler_env.define(error_var, str(e))

                    # Evaluate handler forms in order, return value of last one
                    if len(handler_forms) == 0:
                        return NIL

                    # Evaluate all but the last form
                    for form in handler_forms[:-1]:
                        _trampoline(_seval_internal(form, handler_env))

                    # Last form is in tail position - return it as _TailCall for the outer trampoline
                    return _TailCall(handler_forms[-1], handler_env)

            # If we reach here, head is a Symbol but no special form matched
            # Check for macro expansion
            maybe_macro = env.try_lookup(head)
            if isinstance(maybe_macro, Macro):
                # Expand the macro: apply transformer to unevaluated args
                # Use specialized macro evaluation to reduce stack depth
                expansion = _eval_macro_transformer(maybe_macro.transformer, list(expr[1:]))
                # The macro expansion is evaluated in tail position
                return _TailCall(expansion, env)

        # Not a special form and not a macro (or head is not a Symbol): it's a function call
        # Evaluate the head and all arguments (not in tail position)
        proc = _trampoline(_seval_internal(head, env))
        args = [_trampoline(_seval_internal(arg, env)) for arg in expr[1:]]
        return _apply_proc_internal(proc, args)

    # Self-evaluating: numbers, strings, booleans, etc.
    return expr


def _trampoline(result):
    """Execute tail calls until a final value is reached.

    Args:
        result: Either a final value or a _TailCall object.

    Returns:
        The final value after all tail calls are executed.
    """
    while isinstance(result, _TailCall):
        result = _seval_internal(result.expr, result.env)
    return result


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
    result = _seval_internal(expr, env)
    return _trampoline(result)


def _eval_macro_transformer(transformer, args):
    """Evaluate a macro transformer without full TCO machinery.

    This is a specialized function for macro expansion that avoids nested
    trampoline loops to reduce stack depth.

    Args:
        transformer: A Procedure (the macro transformer).
        args: A list of unevaluated arguments.

    Returns:
        The expanded form.
    """
    # Bind parameters
    if transformer.rest is None:
        if len(args) != len(transformer.params):
            raise EvalError(f"expected {len(transformer.params)} arguments, got {len(args)}")
        call_env = Environment(parent=transformer.env)
        for param, arg in zip(transformer.params, args):
            call_env.define(param, arg)
    else:
        if len(args) < len(transformer.params):
            raise EvalError(f"expected at least {len(transformer.params)} arguments, got {len(args)}")
        call_env = Environment(parent=transformer.env)
        for param, arg in zip(transformer.params, args):
            call_env.define(param, arg)
        rest_args = PebbleList(args[len(transformer.params):])
        call_env.define(transformer.rest, rest_args)

    # Evaluate body with minimal TCO (just one level)
    if len(transformer.body) == 0:
        return NIL
    for form in transformer.body[:-1]:
        _trampoline(_seval_internal(form, call_env))
    # Last form: evaluate it and return the result
    result = _seval_internal(transformer.body[-1], call_env)
    # Use a single trampoline to resolve _TailCall
    return _trampoline(result)


def _apply_proc_internal(proc, args):
    """Internal version of apply_proc that may return _TailCall objects.

    Args:
        proc: A Procedure or a callable (builtin).
        args: A list of evaluated arguments.

    Returns:
        Either a final value or a _TailCall object (for TCO).

    Raises:
        EvalError: If proc is not callable or arity mismatches.
    """
    if isinstance(proc, Procedure):
        # Check arity
        if proc.rest is None:
            # No rest parameter: require exact arity
            if len(args) != len(proc.params):
                raise EvalError(f"expected {len(proc.params)} arguments, got {len(args)}")
            # Create new env with bindings
            call_env = Environment(parent=proc.env)
            for param, arg in zip(proc.params, args):
                call_env.define(param, arg)
        else:
            # Rest parameter: require at least as many args as fixed params
            if len(args) < len(proc.params):
                raise EvalError(f"expected at least {len(proc.params)} arguments, got {len(args)}")
            # Create new env with bindings
            call_env = Environment(parent=proc.env)
            # Bind fixed params
            for param, arg in zip(proc.params, args):
                call_env.define(param, arg)
            # Bind rest param to remaining args as a PebbleList
            rest_args = PebbleList(args[len(proc.params):])
            call_env.define(proc.rest, rest_args)

        # Evaluate body with TCO: only the last form is in tail position
        if len(proc.body) == 0:
            return NIL
        # Process non-final forms (not in tail position)
        for form in proc.body[:-1]:
            _trampoline(_seval_internal(form, call_env))
        # The last form is in tail position: return a _TailCall instead of evaluating it
        # This allows the trampoline to handle it without consuming stack depth
        return _TailCall(proc.body[-1], call_env)

    elif callable(proc):
        # It's a Python function (builtin)
        return proc(*args)

    else:
        raise EvalError(f"not callable: {proc}")


def apply_proc(proc, args):
    """Apply a procedure to arguments.

    This is the public interface. For procedures, it returns a final value
    (trampoline is applied internally). For builtins, it calls them directly.

    Args:
        proc: A Procedure or a callable (builtin).
        args: A list of evaluated arguments.

    Returns:
        The result of the function call.

    Raises:
        EvalError: If proc is not callable or arity mismatches.
    """
    result = _apply_proc_internal(proc, args)
    # Trampoline if we got a _TailCall
    if isinstance(result, _TailCall):
        return _trampoline(result)
    return result


_prelude_cache = None
_template_env_with_prelude = None
_template_env_builtins_only = None

def _load_prelude():
    """Load and parse the prelude source, caching the result.

    Returns:
        A list of parsed forms from the prelude.
    """
    global _prelude_cache
    if _prelude_cache is not None:
        return _prelude_cache

    import os

    # Get the path to prelude.pebble in the pebble package
    prelude_path = os.path.join(os.path.dirname(__file__), 'prelude.pebble')

    with open(prelude_path, 'r') as f:
        source = f.read()

    _prelude_cache = read(source)
    return _prelude_cache


def _build_builtins_only_env():
    """Build a template environment with only primitive builtins.

    Returns:
        An Environment with all primitive builtins defined.
    """
    from pebble.builtins import builtin_table

    env = Environment()
    for name, fn in builtin_table(apply_proc).items():
        env.define(Symbol(name), fn)
    return env


def _build_template_env_with_prelude():
    """Build the template environment with builtins and prelude evaluated.

    This is called once and cached at module level.
    Returns an Environment with all builtins and prelude definitions.
    """
    # Start with builtins-only template
    template_env = _build_builtins_only_env()

    # Evaluate all prelude forms into it
    prelude_forms = _load_prelude()
    for form in prelude_forms:
        seval(form, template_env)

    return template_env


def _get_template_env_with_prelude():
    """Get or lazily build the template environment with prelude.

    Returns:
        The cached template Environment.
    """
    global _template_env_with_prelude
    if _template_env_with_prelude is None:
        _template_env_with_prelude = _build_template_env_with_prelude()
    return _template_env_with_prelude


def _get_template_env_builtins_only():
    """Get or lazily build the template environment with builtins only.

    Returns:
        The cached template Environment.
    """
    global _template_env_builtins_only
    if _template_env_builtins_only is None:
        _template_env_builtins_only = _build_builtins_only_env()
    return _template_env_builtins_only


def make_global_env(load_prelude=True) -> Environment:
    """Create the global environment with primitive builtins.

    Args:
        load_prelude: If True (default), load the standard library prelude.
                     If False, return environment with only primitive builtins.

    Returns:
        An Environment with starter builtins defined, and optionally prelude definitions.
        Each call returns a NEW, INDEPENDENT environment.
    """
    if load_prelude:
        # Get the template with prelude
        template = _get_template_env_with_prelude()
        # Create a new environment with shallow-copied bindings
        # This makes each returned environment independent
        new_env = Environment()
        new_env.vars = template.vars.copy()
        return new_env
    else:
        # Get the template with only builtins
        template = _get_template_env_builtins_only()
        # Create a new environment with shallow-copied bindings
        new_env = Environment()
        new_env.vars = template.vars.copy()
        return new_env


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
