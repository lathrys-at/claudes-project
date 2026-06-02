"""Tests for variadic (rest) parameters in lambdas and macros."""
import pytest
from pebble.evaluator import (
    seval, make_global_env, eval_source, EvalError, Procedure, parse_param_spec
)
from pebble.reader import read_one, read
from pebble.types import Symbol, PebbleList, NIL


class TestParseParamSpec:
    """Tests for the parse_param_spec helper function."""

    def test_bare_symbol(self):
        """Test parsing a bare symbol as parameter spec."""
        spec = Symbol("args")
        fixed, rest = parse_param_spec(spec)
        assert fixed == []
        assert rest == Symbol("args")

    def test_plain_list_no_rest(self):
        """Test parsing a plain list with no dot."""
        spec = PebbleList([Symbol("a"), Symbol("b"), Symbol("c")])
        fixed, rest = parse_param_spec(spec)
        assert fixed == [Symbol("a"), Symbol("b"), Symbol("c")]
        assert rest is None

    def test_dotted_list(self):
        """Test parsing a list with dotted rest syntax."""
        spec = PebbleList([Symbol("a"), Symbol("b"), Symbol("."), Symbol("rest")])
        fixed, rest = parse_param_spec(spec)
        assert fixed == [Symbol("a"), Symbol("b")]
        assert rest == Symbol("rest")

    def test_dotted_list_single_fixed(self):
        """Test parsing a dotted list with single fixed parameter."""
        spec = PebbleList([Symbol("a"), Symbol("."), Symbol("rest")])
        fixed, rest = parse_param_spec(spec)
        assert fixed == [Symbol("a")]
        assert rest == Symbol("rest")

    def test_dotted_list_no_fixed(self):
        """Test parsing a dotted list with no fixed parameters."""
        spec = PebbleList([Symbol("."), Symbol("rest")])
        fixed, rest = parse_param_spec(spec)
        assert fixed == []
        assert rest == Symbol("rest")

    def test_empty_list(self):
        """Test parsing an empty list."""
        spec = PebbleList([])
        fixed, rest = parse_param_spec(spec)
        assert fixed == []
        assert rest is None

    def test_malformed_dot_position(self):
        """Test that dot not in second-to-last position raises error."""
        spec = PebbleList([Symbol("."), Symbol("a"), Symbol("b")])
        with pytest.raises(EvalError, match="dot must be second-to-last"):
            parse_param_spec(spec)

    def test_multiple_dots(self):
        """Test that multiple dots raise error."""
        spec = PebbleList([Symbol("a"), Symbol("."), Symbol("b"), Symbol("."), Symbol("c")])
        with pytest.raises(EvalError, match="multiple dots"):
            parse_param_spec(spec)

    def test_dot_alone_at_end(self):
        """Test that dot at end without rest symbol raises error."""
        spec = PebbleList([Symbol("a"), Symbol(".")])
        with pytest.raises(EvalError, match="dot must be second-to-last"):
            parse_param_spec(spec)

    def test_non_symbol_parameter(self):
        """Test that non-symbol parameters raise error."""
        spec = PebbleList([Symbol("a"), 42])
        with pytest.raises(EvalError, match="parameter must be a symbol"):
            parse_param_spec(spec)

    def test_invalid_spec_type(self):
        """Test that invalid spec type raises error."""
        spec = 42
        with pytest.raises(EvalError, match="invalid parameter specification"):
            parse_param_spec(spec)


class TestBareSymbolParams:
    """Tests for bare-symbol parameter specs (collects all args)."""

    def test_lambda_bare_symbol_three_args(self):
        """Test lambda with bare symbol param collecting three args."""
        env = make_global_env()
        source = "((lambda args args) 1 2 3)"
        result = eval_source(source, env)
        assert result == PebbleList([1, 2, 3])

    def test_lambda_bare_symbol_no_args(self):
        """Test lambda with bare symbol param and no arguments."""
        env = make_global_env()
        source = "((lambda args args))"
        result = eval_source(source, env)
        assert result == NIL

    def test_lambda_bare_symbol_length(self):
        """Test lambda with bare symbol param and length function."""
        env = make_global_env()
        source = "((lambda args (length args)))"
        result = eval_source(source, env)
        assert result == 0

    def test_lambda_bare_symbol_length_three_args(self):
        """Test lambda with bare symbol param and length with multiple args."""
        env = make_global_env()
        source = "((lambda args (length args)) 1 2 3)"
        result = eval_source(source, env)
        assert result == 3

    def test_lambda_bare_symbol_single_arg(self):
        """Test lambda with bare symbol param and single arg."""
        env = make_global_env()
        source = "((lambda args args) 99)"
        result = eval_source(source, env)
        assert result == PebbleList([99])


class TestDottedRestParams:
    """Tests for dotted rest parameter syntax (a b . rest)."""

    def test_lambda_dotted_rest_basic(self):
        """Test lambda with dotted rest collecting some args."""
        env = make_global_env()
        source = "((lambda (a b . rest) rest) 1 2 3 4)"
        result = eval_source(source, env)
        assert result == PebbleList([3, 4])

    def test_lambda_dotted_rest_exact_fixed_count(self):
        """Test lambda with dotted rest when given exactly the fixed count."""
        env = make_global_env()
        source = "((lambda (a b . rest) rest) 1 2)"
        result = eval_source(source, env)
        assert result == NIL

    def test_lambda_dotted_rest_single_fixed(self):
        """Test lambda with single fixed and dotted rest."""
        env = make_global_env()
        source = "((lambda (a . rest) a) 10 20 30)"
        result = eval_source(source, env)
        assert result == 10

    def test_lambda_dotted_rest_returns_fixed_and_rest(self):
        """Test lambda returning both fixed and rest params."""
        env = make_global_env()
        source = "((lambda (a b . rest) (list a b rest)) 1 2 3 4)"
        result = eval_source(source, env)
        assert result == PebbleList([1, 2, PebbleList([3, 4])])

    def test_lambda_dotted_rest_too_few_args(self):
        """Test that dotted rest with too few args raises error."""
        env = make_global_env()
        source = "((lambda (a b . rest) a) 1)"
        with pytest.raises(EvalError, match="expected at least 2 arguments, got 1"):
            eval_source(source, env)

    def test_lambda_dotted_rest_no_fixed(self):
        """Test dotted rest with no fixed parameters."""
        env = make_global_env()
        source = "((lambda (. rest) rest) 1 2 3)"
        result = eval_source(source, env)
        assert result == PebbleList([1, 2, 3])


class TestNonVariadicRegression:
    """Tests to ensure non-variadic lambdas still enforce exact arity."""

    def test_lambda_exact_arity_enforcement(self):
        """Test that non-variadic lambda still requires exact arity."""
        env = make_global_env()
        source = "((lambda (x) x) 1 2)"
        with pytest.raises(EvalError, match="expected 1 arguments, got 2"):
            eval_source(source, env)

    def test_lambda_exact_arity_too_few(self):
        """Test that non-variadic lambda with too few args raises error."""
        env = make_global_env()
        source = "((lambda (x y) x))"
        with pytest.raises(EvalError, match="expected 2 arguments, got 0"):
            eval_source(source, env)

    def test_lambda_exact_arity_exact(self):
        """Test that non-variadic lambda works with exact arity."""
        env = make_global_env()
        source = "((lambda (x y) x) 1 2)"
        result = eval_source(source, env)
        assert result == 1


class TestVariadicDefinedFunctions:
    """Tests for variadic functions defined with define and lambda."""

    def test_define_variadic_function_no_args(self):
        """Test defining and calling a variadic function with no args."""
        env = make_global_env()
        source = """
        (define sum-all (lambda xs (foldl + 0 xs)))
        (sum-all)
        """
        result = eval_source(source, env)
        assert result == 0

    def test_define_variadic_function_single_arg(self):
        """Test defining and calling a variadic function with single arg."""
        env = make_global_env()
        source = """
        (define sum-all (lambda xs (foldl + 0 xs)))
        (sum-all 5)
        """
        result = eval_source(source, env)
        assert result == 5

    def test_define_variadic_function_multiple_args(self):
        """Test defining and calling a variadic function with multiple args."""
        env = make_global_env()
        source = """
        (define sum-all (lambda xs (foldl + 0 xs)))
        (sum-all 1 2 3 4)
        """
        result = eval_source(source, env)
        assert result == 10

    def test_define_variadic_function_with_fixed(self):
        """Test defining a variadic function with fixed and rest params."""
        env = make_global_env()
        source = """
        (define cons-with-prefix (lambda (prefix . rest) (cons prefix rest)))
        (cons-with-prefix "x" 1 2 3)
        """
        result = eval_source(source, env)
        assert result == PebbleList(["x", 1, 2, 3])


class TestVariadicMacros:
    """Tests for variadic macros."""

    def test_variadic_macro_with_body_rest(self):
        """Test a variadic macro like when that collects body expressions."""
        env = make_global_env()
        source = """
        (define-macro (when test . body)
          `(if ,test (begin ,@body) nil))
        (when true 1 2 3)
        """
        result = eval_source(source, env)
        assert result == 3

    def test_variadic_macro_when_false(self):
        """Test when macro with false condition."""
        env = make_global_env()
        source = """
        (define-macro (when test . body)
          `(if ,test (begin ,@body) nil))
        (when false 1 2 3)
        """
        result = eval_source(source, env)
        assert result == NIL

    def test_variadic_macro_with_side_effects(self):
        """Test variadic macro with side effects in body."""
        env = make_global_env()
        source = """
        (define-macro (when test . body)
          `(if ,test (begin ,@body) nil))
        (define x 0)
        (when true (set! x 1) (set! x 2) (set! x 3))
        x
        """
        result = eval_source(source, env)
        assert result == 3

    def test_variadic_macro_unless(self):
        """Test variadic unless macro (only executes if condition is false)."""
        env = make_global_env()
        source = """
        (define-macro (unless test . body)
          `(if ,test nil (begin ,@body)))
        (unless false 1 2 3)
        """
        result = eval_source(source, env)
        assert result == 3

    def test_variadic_macro_unless_true(self):
        """Test variadic unless macro with true condition."""
        env = make_global_env()
        source = """
        (define-macro (unless test . body)
          `(if ,test nil (begin ,@body)))
        (unless true 1 2 3)
        """
        result = eval_source(source, env)
        assert result == NIL

    def test_variadic_macro_no_body_args(self):
        """Test variadic macro with no body arguments."""
        env = make_global_env()
        source = """
        (define-macro (when test . body)
          `(if ,test (begin ,@body) nil))
        (when true)
        """
        result = eval_source(source, env)
        assert result == NIL


class TestProcedureRepr:
    """Tests for Procedure string representation with rest params."""

    def test_procedure_repr_bare_symbol(self):
        """Test Procedure repr with bare symbol rest param."""
        env = make_global_env()
        proc = Procedure([], [], env, rest=Symbol("args"))
        assert "args" in repr(proc)
        assert "procedure" in repr(proc)

    def test_procedure_repr_dotted_rest(self):
        """Test Procedure repr with dotted rest syntax."""
        env = make_global_env()
        proc = Procedure([Symbol("a"), Symbol("b")], [], env, rest=Symbol("rest"))
        repr_str = repr(proc)
        assert "a" in repr_str
        assert "b" in repr_str
        assert "rest" in repr_str
        assert "." in repr_str

    def test_procedure_repr_no_rest(self):
        """Test Procedure repr without rest param (unchanged)."""
        env = make_global_env()
        proc = Procedure([Symbol("x"), Symbol("y")], [], env)
        repr_str = repr(proc)
        assert "x" in repr_str
        assert "y" in repr_str
        assert "procedure" in repr_str


class TestBackwardCompatibility:
    """Tests ensuring backward compatibility with 3-argument Procedure calls."""

    def test_procedure_three_arg_constructor(self):
        """Test that Procedure can still be constructed with 3 args."""
        env = make_global_env()
        # This should work without passing rest=None explicitly
        proc = Procedure([Symbol("x")], [Symbol("x")], env)
        assert proc.rest is None
        assert proc.params == [Symbol("x")]

    def test_existing_test_compatibility(self):
        """Test that existing test patterns still work."""
        env = make_global_env()
        # From test_macros.py - should still work
        proc = Procedure([], [Symbol("nil")], env)
        assert proc.rest is None
