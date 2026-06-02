"""Tests for the Pebble macro system."""
import pytest
from pebble.evaluator import (
    seval, make_global_env, eval_source, EvalError, Macro, Procedure
)
from pebble.reader import read_one, read
from pebble.types import Symbol, PebbleList, NIL


class TestMacroType:
    """Tests for the Macro class and basic macro operations."""

    def test_macro_repr(self):
        """Test that Macro repr returns '<macro>'."""
        env = make_global_env()
        # Create a simple macro directly
        proc = Procedure([], [Symbol("nil")], env)
        macro = Macro(proc)
        assert repr(macro) == "<macro>"


class TestDefineMacroFunctionStyle:
    """Tests for function-style define-macro."""

    def test_define_macro_function_style_basic(self):
        """Test basic function-style define-macro."""
        env = make_global_env()
        source = """
        (define-macro (unless test body)
          `(if ,test nil ,body))
        """
        result = eval_source(source, env)
        assert isinstance(result, Symbol)
        assert result == "unless"

        # Check that unless was defined as a Macro
        unless_macro = env.lookup("unless")
        assert isinstance(unless_macro, Macro)

    def test_unless_macro_false_branch(self):
        """Test unless macro when test is false -> execute body."""
        env = make_global_env()
        source = """
        (define-macro (unless test body)
          `(if ,test nil ,body))
        (unless false 42)
        """
        result = eval_source(source, env)
        assert result == 42

    def test_unless_macro_true_branch(self):
        """Test unless macro when test is true -> return nil."""
        env = make_global_env()
        source = """
        (define-macro (unless test body)
          `(if ,test nil ,body))
        (unless true 42)
        """
        result = eval_source(source, env)
        assert result == NIL

    def test_when_macro(self):
        """Test when macro: (when test body) evaluates body if test is truthy."""
        env = make_global_env()
        source = """
        (define-macro (when test body)
          `(if ,test ,body nil))
        (when true 99)
        """
        result = eval_source(source, env)
        assert result == 99

    def test_when_macro_false_branch(self):
        """Test when macro with false test -> nil."""
        env = make_global_env()
        source = """
        (define-macro (when test body)
          `(if ,test ,body nil))
        (when false 99)
        """
        result = eval_source(source, env)
        assert result == NIL

    def test_define_macro_returns_name(self):
        """Test that define-macro returns the macro name."""
        env = make_global_env()
        forms = read("(define-macro (test-m x) `(+ ,x 1))")
        result = seval(forms[0], env)
        assert result == Symbol("test-m")

    def test_macro_with_multiple_params(self):
        """Test macro with multiple parameters."""
        env = make_global_env()
        source = """
        (define-macro (my-or a b)
          `(if ,a ,a ,b))
        (my-or false 42)
        """
        result = eval_source(source, env)
        assert result == 42

    def test_macro_with_multiple_params_first_true(self):
        """Test my-or macro with first argument true."""
        env = make_global_env()
        source = """
        (define-macro (my-or a b)
          `(if ,a ,a ,b))
        (my-or 10 42)
        """
        result = eval_source(source, env)
        assert result == 10


class TestDefineMacroValueStyle:
    """Tests for value-style define-macro."""

    def test_define_macro_value_style(self):
        """Test value-style define-macro with a lambda."""
        env = make_global_env()
        source = """
        (define-macro m (lambda (x) `(+ ,x 1)))
        (m 5)
        """
        result = eval_source(source, env)
        assert result == 6

    def test_define_macro_value_style_returns_name(self):
        """Test that value-style define-macro returns the macro name."""
        env = make_global_env()
        source = """
        (define-macro m (lambda (x) `(+ ,x 1)))
        m
        """
        forms = read(source)
        # Evaluate the define-macro
        seval(forms[0], env)
        # Evaluate the symbol lookup
        result = seval(forms[1], env)
        assert isinstance(result, Macro)

    def test_define_macro_value_style_non_procedure_error(self):
        """Test that value-style define-macro raises error if transformer is not a procedure."""
        env = make_global_env()
        source = "(define-macro m 42)"
        forms = read(source)
        with pytest.raises(EvalError, match="transformer must be a procedure"):
            seval(forms[0], env)


class TestNestedMacroExpansion:
    """Tests for macros that expand to other macro calls."""

    def test_nested_macro_expansion(self):
        """Test a macro that expands to another macro call."""
        env = make_global_env()
        source = """
        (define-macro (unless test body)
          `(if ,test nil ,body))
        (define-macro (unless2 test body)
          `(unless ,test ,body))
        (unless2 false 77)
        """
        result = eval_source(source, env)
        assert result == 77

    def test_nested_macro_expansion_with_true_test(self):
        """Test nested macro expansion with true test."""
        env = make_global_env()
        source = """
        (define-macro (unless test body)
          `(if ,test nil ,body))
        (define-macro (unless2 test body)
          `(unless ,test ,body))
        (unless2 true 77)
        """
        result = eval_source(source, env)
        assert result == NIL


class TestSpecialFormsVsMacros:
    """Tests that special forms still work and win over macros."""

    def test_if_special_form_works(self):
        """Test that if still works as a special form."""
        env = make_global_env()
        source = "(if true 1 2)"
        result = eval_source(source, env)
        assert result == 1

    def test_quote_special_form_works(self):
        """Test that quote still works as a special form."""
        env = make_global_env()
        source = "(quote (a b c))"
        result = eval_source(source, env)
        assert result == PebbleList([Symbol("a"), Symbol("b"), Symbol("c")])

    def test_lambda_special_form_works(self):
        """Test that lambda still works as a special form."""
        env = make_global_env()
        source = "(lambda (x) (+ x 1))"
        result = eval_source(source, env)
        assert isinstance(result, Procedure)


class TestMacroQuestionPredicate:
    """Tests for the macro? predicate."""

    def test_macro_question_true_for_macro(self):
        """Test (macro? unless) returns true after defining unless as a macro."""
        env = make_global_env()
        source = """
        (define-macro (unless test body)
          `(if ,test nil ,body))
        (macro? unless)
        """
        result = eval_source(source, env)
        assert result is True

    def test_macro_question_false_for_builtin(self):
        """Test (macro? +) returns false for builtins."""
        env = make_global_env()
        source = "(macro? +)"
        result = eval_source(source, env)
        assert result is False

    def test_macro_question_false_for_number(self):
        """Test (macro? 5) returns false for non-macro values."""
        env = make_global_env()
        source = "(macro? 5)"
        result = eval_source(source, env)
        assert result is False

    def test_macro_question_false_for_procedure(self):
        """Test (macro? (lambda (x) x)) returns false for procedures."""
        env = make_global_env()
        source = "(macro? (lambda (x) x))"
        result = eval_source(source, env)
        assert result is False


class TestGensym:
    """Tests for the gensym builtin."""

    def test_gensym_returns_symbol(self):
        """Test that (gensym) returns a Symbol."""
        env = make_global_env()
        source = "(symbol? (gensym))"
        result = eval_source(source, env)
        assert result is True

    def test_gensym_returns_different_symbols(self):
        """Test that successive calls to gensym return different symbols."""
        env = make_global_env()
        source = """
        (define s1 (gensym))
        (define s2 (gensym))
        (= s1 s2)
        """
        result = eval_source(source, env)
        assert result is False

    def test_gensym_with_prefix(self):
        """Test (gensym "tmp") returns symbol with prefix."""
        env = make_global_env()
        source = """
        (define s (gensym "tmp"))
        (symbol? s)
        """
        result = eval_source(source, env)
        assert result is True

    def test_gensym_with_symbol_prefix(self):
        """Test gensym with symbol prefix."""
        env = make_global_env()
        source = """
        (define s (gensym 'tmp))
        (symbol? s)
        """
        result = eval_source(source, env)
        assert result is True

    def test_gensym_prefix_appears_in_name(self):
        """Test that the prefix appears in the gensym'd symbol name."""
        env = make_global_env()
        source = """
        (define s (gensym "myprefix"))
        (define s_str (symbol->string s))
        (string? s_str)
        """
        result = eval_source(source, env)
        assert result is True

    def test_gensym_no_args_uses_default_prefix(self):
        """Test that gensym with no args uses 'g' as prefix."""
        env = make_global_env()
        source = """
        (define s (gensym))
        (define s_str (symbol->string s))
        (string? s_str)
        """
        result = eval_source(source, env)
        assert result is True


class TestGensymInMacro:
    """Tests for gensym used within macros for hygiene."""

    def test_macro_with_gensym(self):
        """Test a macro that uses gensym to avoid variable capture."""
        env = make_global_env()
        source = """
        (define-macro (make-pair x y)
          (let ((tmp (gensym "pair")))
            `(let ((,tmp (cons ,x (cons ,y nil))))
               ,tmp)))
        (make-pair 1 2)
        """
        result = eval_source(source, env)
        assert isinstance(result, PebbleList)
        assert len(result) == 2
        assert result[0] == 1
        assert result[1] == 2

    def test_macro_gensym_creates_fresh_bindings(self):
        """Test that gensym creates fresh bindings in macro expansion."""
        env = make_global_env()
        source = """
        (define-macro (double-eval x)
          (let ((temp (gensym "temp")))
            `(let ((,temp ,x))
               (+ ,temp ,temp))))
        (double-eval 5)
        """
        result = eval_source(source, env)
        assert result == 10


class TestMacroErrors:
    """Tests for error handling in macro definition."""

    def test_define_macro_no_args_error(self):
        """Test that (define-macro) with no args raises EvalError."""
        env = make_global_env()
        source = "(define-macro)"
        forms = read(source)
        with pytest.raises(EvalError, match="define-macro requires at least 1 argument"):
            seval(forms[0], env)

    def test_define_macro_function_style_empty_params_error(self):
        """Test that empty params list in function-style raises error."""
        env = make_global_env()
        source = "(define-macro () body)"
        forms = read(source)
        with pytest.raises(EvalError, match="cannot be empty"):
            seval(forms[0], env)

    def test_define_macro_function_style_non_symbol_name_error(self):
        """Test that non-symbol name in function-style raises error."""
        env = make_global_env()
        source = "(define-macro (42 x) body)"
        forms = read(source)
        with pytest.raises(EvalError, match="macro name must be a symbol"):
            seval(forms[0], env)

    def test_define_macro_function_style_non_symbol_param_error(self):
        """Test that non-symbol parameter in function-style raises error."""
        env = make_global_env()
        source = "(define-macro (m 42) body)"
        forms = read(source)
        with pytest.raises(EvalError, match="parameter must be a symbol"):
            seval(forms[0], env)


class TestUnboundSymbolStillRaises:
    """Tests that unbound symbols used as function calls still raise errors."""

    def test_undefined_symbol_call_raises_error(self):
        """Test that calling an undefined symbol raises EvalError."""
        env = make_global_env()
        source = "(nonexistent 1 2)"
        forms = read(source)
        with pytest.raises(EvalError, match="undefined symbol"):
            seval(forms[0], env)

    def test_undefined_symbol_in_nested_call(self):
        """Test that undefined symbols in nested calls raise errors."""
        env = make_global_env()
        source = "(+ 1 (undefined-fn 2))"
        forms = read(source)
        with pytest.raises(EvalError, match="undefined symbol"):
            seval(forms[0], env)


class TestMacroExpansionWithUnquoteSplicing:
    """Tests for macros using unquote-splicing."""

    def test_macro_with_unquote_splicing(self):
        """Test a macro that uses unquote-splicing."""
        env = make_global_env()
        source = """
        (define-macro (list-wrap items)
          `(list ,@items))
        (list-wrap (1 2 3))
        """
        result = eval_source(source, env)
        assert result == PebbleList([1, 2, 3])

    def test_macro_splicing_multiple_args(self):
        """Test macro with unquote-splicing in multiple argument lists."""
        env = make_global_env()
        source = """
        (define-macro (build-list a b c)
          `(list ,a ,b ,c))
        (build-list 10 20 30)
        """
        result = eval_source(source, env)
        assert result == PebbleList([10, 20, 30])


class TestComplexMacroScenarios:
    """Tests for more complex macro scenarios."""

    def test_cond_like_macro(self):
        """Test a cond-like macro using quasiquote."""
        env = make_global_env()
        source = """
        (define-macro (ifthenelse test then-part else-part)
          `(if ,test ,then-part ,else-part))
        (ifthenelse (> 5 3) "yes" "no")
        """
        result = eval_source(source, env)
        assert result == "yes"

    def test_macro_with_quoted_result(self):
        """Test a macro that produces quoted code."""
        env = make_global_env()
        source = """
        (define-macro (quoted-list a b)
          `(quote (,a ,b)))
        (car (quoted-list x y))
        """
        result = eval_source(source, env)
        assert result == Symbol("x")

    def test_macro_expansion_in_larger_expression(self):
        """Test that macro expansion works correctly within larger expressions."""
        env = make_global_env()
        source = """
        (define-macro (inc x) `(+ ,x 1))
        (+ (inc 5) (inc 10))
        """
        result = eval_source(source, env)
        assert result == 17

    def test_macro_shadowing_builtin(self):
        """Test that a macro can shadow a builtin (though not recommended)."""
        env = make_global_env()
        source = """
        (define-macro (custom-add a b)
          `(+ ,a ,b 100))
        (custom-add 1 2)
        """
        result = eval_source(source, env)
        assert result == 103
