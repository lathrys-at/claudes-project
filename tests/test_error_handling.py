"""Tests for try/catch error handling special form."""
import pytest
from pebble.evaluator import seval, make_global_env, EvalError
from pebble.reader import read_one
from pebble.types import Symbol, PebbleList, NIL


class TestTryCatchSuccess:
    """Tests for successful try/catch evaluation (no error)."""

    def test_try_catches_explicit_error(self):
        """Catching an explicit error from the error builtin."""
        env = make_global_env()
        code = read_one('(try (error "boom") (catch e e))')
        result = seval(code, env)
        assert result == "boom"

    def test_try_success_path_returns_expr_value(self):
        """When expr succeeds, try returns expr's value and doesn't run handler."""
        env = make_global_env()
        code = read_one('(try (+ 1 2) (catch e 0))')
        result = seval(code, env)
        assert result == 3

    def test_try_success_handler_side_effects_dont_occur(self):
        """Handler side effects should not occur on success."""
        env = make_global_env()
        # Define a flag, then evaluate (try 42 (catch e (set! flag true)))
        # The flag should remain false
        seval(read_one('(define flag false)'), env)
        code = read_one('(try 42 (catch e (set! flag true)))')
        result = seval(code, env)
        assert result == 42
        # Verify the flag was NOT set
        flag_val = seval(read_one('flag'), env)
        assert flag_val is False


class TestTryCatchMessage:
    """Tests for error message binding in catch handlers."""

    def test_catch_uses_error_message(self):
        """The caught error message should be available in handler."""
        env = make_global_env()
        code = read_one('(try (error "boom") (catch e (string-append "caught: " e)))')
        result = seval(code, env)
        assert result == "caught: boom"

    def test_catch_binds_string_value(self):
        """The error variable should be a string."""
        env = make_global_env()
        code = read_one('(try (error "test msg") (catch e (string? e)))')
        result = seval(code, env)
        assert result is True


class TestTryCatchRuntimeErrors:
    """Tests for catching runtime errors."""

    def test_catch_division_by_zero(self):
        """Catching a division-by-zero runtime error."""
        env = make_global_env()
        code = read_one('(try (/ 1 0) (catch e e))')
        result = seval(code, env)
        assert isinstance(result, str)
        assert "division by zero" in result

    def test_catch_car_empty_list(self):
        """Catching car called on empty list."""
        env = make_global_env()
        code = read_one('(try (car (list)) (catch e e))')
        result = seval(code, env)
        assert isinstance(result, str)
        assert "car" in result

    def test_catch_undefined_symbol(self):
        """Catching undefined symbol lookup."""
        env = make_global_env()
        code = read_one('(try some-undefined-variable (catch e e))')
        result = seval(code, env)
        assert isinstance(result, str)
        assert "undefined" in result


class TestTryCatchMultipleHandlerForms:
    """Tests for multiple forms in handler."""

    def test_handler_returns_last_form_value(self):
        """Handler should return the value of the last form."""
        env = make_global_env()
        code = read_one('(try (error "x") (catch e (+ 1 2) (+ 3 4)))')
        result = seval(code, env)
        assert result == 7

    def test_handler_earlier_forms_execute(self):
        """Earlier handler forms should execute (verify via side effect)."""
        env = make_global_env()
        seval(read_one('(define counter 0)'), env)
        code = read_one(
            '(try (error "x") (catch e (set! counter (+ counter 1)) (set! counter (+ counter 1)) counter))'
        )
        result = seval(code, env)
        assert result == 2
        # Verify side effect happened
        counter = seval(read_one('counter'), env)
        assert counter == 2


class TestTryCatchScoping:
    """Tests for catch variable scoping."""

    def test_catch_variable_not_defined_after(self):
        """The catch variable should not be defined in outer scope after try."""
        env = make_global_env()
        seval(read_one('(try (error "x") (catch e e))'), env)
        # Now trying to reference e should raise an error
        with pytest.raises(EvalError, match="undefined symbol"):
            seval(read_one('e'), env)

    def test_catch_variable_isolated_scope(self):
        """Catch variable is scoped to the handler only."""
        env = make_global_env()
        # Define e in outer scope
        seval(read_one('(define e "outer")'), env)
        # The catch should create a new binding in its own scope
        code = read_one('(try (error "inner") (catch e e))')
        result = seval(code, env)
        assert result == "inner"
        # The outer e should still be "outer"
        outer_e = seval(read_one('e'), env)
        assert outer_e == "outer"


class TestTryCatchNested:
    """Tests for nested try/catch forms."""

    def test_inner_try_catches_its_error(self):
        """Inner try catches its error, outer try not triggered."""
        env = make_global_env()
        code = read_one(
            '(try (try (error "inner") (catch e "caught")) (catch e "outer"))'
        )
        result = seval(code, env)
        assert result == "caught"

    def test_error_in_handler_propagates_to_outer_try(self):
        """An error raised inside a handler propagates to an enclosing try."""
        env = make_global_env()
        code = read_one(
            '(try (try (error "inner") (catch e (error "handler-error"))) (catch e e))'
        )
        result = seval(code, env)
        assert result == "handler-error"


class TestTryCatchWithoutTry:
    """Tests for error behavior without try/catch."""

    def test_error_without_try_propagates(self):
        """An error call with no surrounding try still propagates."""
        env = make_global_env()
        code = read_one('(error "test")')
        with pytest.raises(EvalError, match="test"):
            seval(code, env)


class TestTryCatchMalformed:
    """Tests for malformed try/catch expressions."""

    def test_try_without_catch_clause(self):
        """A try form without a catch clause is malformed."""
        env = make_global_env()
        code = read_one('(try 1)')
        with pytest.raises(EvalError, match="catch"):
            seval(code, env)

    def test_catch_with_non_symbol_name(self):
        """A catch clause with a non-symbol name is malformed."""
        env = make_global_env()
        code = read_one('(try (error "x") (catch 42 42))')
        with pytest.raises(EvalError, match="symbol"):
            seval(code, env)

    def test_catch_missing_literal_catch(self):
        """A catch clause that doesn't start with 'catch' is malformed."""
        env = make_global_env()
        code = read_one('(try (error "x") (not-catch e e))')
        with pytest.raises(EvalError, match="catch"):
            seval(code, env)


class TestTryCatchEmptyHandler:
    """Tests for empty handler body."""

    def test_empty_handler_returns_nil(self):
        """An empty handler (catch e) should return nil."""
        env = make_global_env()
        code = read_one('(try (error "x") (catch e))')
        result = seval(code, env)
        assert result is NIL
