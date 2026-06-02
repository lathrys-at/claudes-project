"""Tests for the Pebble builtins."""
import pytest
from pebble.evaluator import make_global_env, eval_source, EvalError, seval, Procedure
from pebble.reader import read_one
from pebble.types import Symbol, PebbleList, NIL


class TestArithmetic:
    """Tests for arithmetic builtins."""

    def test_modulo(self):
        expr = read_one("(modulo 10 3)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 1

    def test_modulo_zero_divisor(self):
        expr = read_one("(modulo 10 0)")
        env = make_global_env()
        with pytest.raises(EvalError, match="division by zero"):
            seval(expr, env)

    def test_abs_positive(self):
        expr = read_one("(abs 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 42

    def test_abs_negative(self):
        expr = read_one("(abs -42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 42

    def test_abs_zero(self):
        expr = read_one("(abs 0)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 0

    def test_min_single_arg(self):
        expr = read_one("(min 5)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 5

    def test_min_multiple_args(self):
        expr = read_one("(min 3 1 4 1 5)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 1

    def test_min_no_args(self):
        expr = read_one("(min)")
        env = make_global_env()
        with pytest.raises(EvalError, match="min requires at least 1 argument"):
            seval(expr, env)

    def test_max_single_arg(self):
        expr = read_one("(max 5)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 5

    def test_max_multiple_args(self):
        expr = read_one("(max 3 1 4 1 5)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 5

    def test_max_no_args(self):
        expr = read_one("(max)")
        env = make_global_env()
        with pytest.raises(EvalError, match="max requires at least 1 argument"):
            seval(expr, env)

    def test_expt(self):
        expr = read_one("(expt 2 3)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 8

    def test_expt_zero(self):
        expr = read_one("(expt 5 0)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 1

    def test_expt_negative(self):
        expr = read_one("(expt 2 -1)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 0.5


class TestBoolean:
    """Tests for boolean builtins."""

    def test_not_false(self):
        expr = read_one("(not false)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_not_true(self):
        expr = read_one("(not true)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_not_zero_is_false(self):
        """0 is truthy, so (not 0) is False."""
        expr = read_one("(not 0)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_not_nil_is_true(self):
        """nil is falsy, so (not nil) is True."""
        expr = read_one("(not nil)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_not_empty_string_is_false(self):
        """Empty string is truthy, so (not "") is False."""
        expr = read_one('(not "")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is False


class TestTypePredicates:
    """Tests for type predicate builtins."""

    # number?
    def test_number_p_int(self):
        expr = read_one("(number? 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_number_p_float(self):
        expr = read_one("(number? 3.14)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_number_p_bool_false(self):
        """bool should NOT count as a number."""
        expr = read_one("(number? false)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_number_p_bool_true(self):
        """bool should NOT count as a number."""
        expr = read_one("(number? true)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_number_p_string(self):
        expr = read_one('(number? "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # integer?
    def test_integer_p_int(self):
        expr = read_one("(integer? 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_integer_p_float(self):
        expr = read_one("(integer? 3.14)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_integer_p_bool(self):
        """bool should NOT count as integer."""
        expr = read_one("(integer? true)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # float?
    def test_float_p_float(self):
        expr = read_one("(float? 3.14)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_float_p_int(self):
        expr = read_one("(float? 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # string?
    def test_string_p_string(self):
        expr = read_one('(string? "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_string_p_symbol(self):
        """Symbol should NOT count as string."""
        expr = read_one("(string? 'x)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_string_p_number(self):
        expr = read_one("(string? 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # symbol?
    def test_symbol_p_symbol(self):
        expr = read_one("(symbol? 'x)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_symbol_p_string(self):
        expr = read_one('(symbol? "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_symbol_p_number(self):
        expr = read_one("(symbol? 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # list?
    def test_list_p_list(self):
        expr = read_one("(list? (list 1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_list_p_nil(self):
        expr = read_one("(list? nil)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_list_p_number(self):
        expr = read_one("(list? 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # pair?
    def test_pair_p_nonempty_list(self):
        expr = read_one("(pair? (list 1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_pair_p_single_element(self):
        expr = read_one("(pair? (list 1))")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_pair_p_empty_list(self):
        """Empty list is not a pair."""
        expr = read_one("(pair? nil)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # null?
    def test_null_p_empty_list(self):
        expr = read_one("(null? nil)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_null_p_nonempty_list(self):
        expr = read_one("(null? (list 1))")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # nil?
    def test_nil_p_empty_list(self):
        expr = read_one("(nil? nil)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_nil_p_nonempty_list(self):
        expr = read_one("(nil? (list 1))")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # boolean?
    def test_boolean_p_true(self):
        expr = read_one("(boolean? true)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_boolean_p_false(self):
        expr = read_one("(boolean? false)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_boolean_p_number(self):
        expr = read_one("(boolean? 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    def test_boolean_p_string(self):
        expr = read_one('(boolean? "hello")')
        env = make_global_env()
        result = seval(expr, env)
        assert result is False

    # procedure?
    def test_procedure_p_builtin(self):
        expr = read_one("(procedure? +)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is True

    def test_procedure_p_lambda(self):
        env = make_global_env()
        seval(read_one("(define f (lambda (x) x))"), env)
        expr = read_one("(procedure? f)")
        result = seval(expr, env)
        assert result is True

    def test_procedure_p_number(self):
        expr = read_one("(procedure? 42)")
        env = make_global_env()
        result = seval(expr, env)
        assert result is False


class TestListOperations:
    """Tests for list operation builtins."""

    def test_length(self):
        expr = read_one("(length (list 1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 3

    def test_length_empty(self):
        expr = read_one("(length nil)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 0

    def test_length_non_list(self):
        expr = read_one("(length 42)")
        env = make_global_env()
        with pytest.raises(EvalError, match="length: argument must be a list"):
            seval(expr, env)

    def test_append_single_list(self):
        expr = read_one("(append (list 1 2))")
        env = make_global_env()
        result = seval(expr, env)
        assert list(result) == [1, 2]

    def test_append_multiple_lists(self):
        expr = read_one("(append (list 1 2) (list 3 4) (list 5))")
        env = make_global_env()
        result = seval(expr, env)
        assert list(result) == [1, 2, 3, 4, 5]

    def test_append_empty(self):
        expr = read_one("(append)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == NIL

    def test_append_non_list(self):
        expr = read_one("(append (list 1) 42)")
        env = make_global_env()
        with pytest.raises(EvalError, match="append: argument must be a list"):
            seval(expr, env)

    def test_reverse(self):
        expr = read_one("(reverse (list 1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert list(result) == [3, 2, 1]

    def test_reverse_empty(self):
        expr = read_one("(reverse nil)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == NIL

    def test_reverse_non_list(self):
        expr = read_one("(reverse 42)")
        env = make_global_env()
        with pytest.raises(EvalError, match="reverse: argument must be a list"):
            seval(expr, env)

    def test_list_ref(self):
        expr = read_one("(list-ref (list 10 20 30) 1)")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 20

    def test_list_ref_out_of_range(self):
        expr = read_one("(list-ref (list 10 20) 5)")
        env = make_global_env()
        with pytest.raises(EvalError, match="list-ref: index .* out of range"):
            seval(expr, env)

    def test_list_ref_non_list(self):
        expr = read_one("(list-ref 42 0)")
        env = make_global_env()
        with pytest.raises(EvalError, match="list-ref: first argument must be a list"):
            seval(expr, env)

    def test_member_found(self):
        expr = read_one("(member 2 (list 1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert list(result) == [2, 3]

    def test_member_not_found(self):
        expr = read_one("(member 5 (list 1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == NIL

    def test_member_first_element(self):
        expr = read_one("(member 1 (list 1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert list(result) == [1, 2, 3]

    def test_member_non_list(self):
        expr = read_one("(member 1 42)")
        env = make_global_env()
        with pytest.raises(EvalError, match="member: second argument must be a list"):
            seval(expr, env)


class TestHigherOrder:
    """Tests for higher-order function builtins."""

    def test_map(self):
        env = make_global_env()
        expr = read_one("(map (lambda (x) (* x x)) (list 1 2 3))")
        result = seval(expr, env)
        assert list(result) == [1, 4, 9]

    def test_map_empty_list(self):
        env = make_global_env()
        expr = read_one("(map (lambda (x) (* x x)) nil)")
        result = seval(expr, env)
        assert result == NIL

    def test_map_non_list(self):
        env = make_global_env()
        expr = read_one("(map (lambda (x) x) 42)")
        with pytest.raises(EvalError, match="map: second argument must be a list"):
            seval(expr, env)

    def test_filter(self):
        env = make_global_env()
        expr = read_one("(filter (lambda (x) (> x 2)) (list 1 2 3 4))")
        result = seval(expr, env)
        assert list(result) == [3, 4]

    def test_filter_empty_list(self):
        env = make_global_env()
        expr = read_one("(filter (lambda (x) (> x 2)) nil)")
        result = seval(expr, env)
        assert result == NIL

    def test_filter_none_match(self):
        env = make_global_env()
        expr = read_one("(filter (lambda (x) (> x 10)) (list 1 2 3))")
        result = seval(expr, env)
        assert result == NIL

    def test_filter_non_list(self):
        env = make_global_env()
        expr = read_one("(filter (lambda (x) true) 42)")
        with pytest.raises(EvalError, match="filter: second argument must be a list"):
            seval(expr, env)

    def test_foldl(self):
        env = make_global_env()
        expr = read_one("(foldl + 0 (list 1 2 3 4))")
        result = seval(expr, env)
        assert result == 10

    def test_foldl_empty(self):
        env = make_global_env()
        expr = read_one("(foldl + 100 nil)")
        result = seval(expr, env)
        assert result == 100

    def test_foldl_non_list(self):
        env = make_global_env()
        expr = read_one("(foldl + 0 42)")
        with pytest.raises(EvalError, match="foldl: third argument must be a list"):
            seval(expr, env)

    def test_foldr(self):
        env = make_global_env()
        # Test order: (foldr cons nil (list 1 2 3)) should give (1 2 3)
        expr = read_one("(foldr cons nil (list 1 2 3))")
        result = seval(expr, env)
        assert list(result) == [1, 2, 3]

    def test_foldr_subtraction(self):
        env = make_global_env()
        # (foldr - 0 (list 1 2 3)) = 1 - (2 - (3 - 0)) = 1 - (2 - 3) = 1 - (-1) = 2
        expr = read_one("(foldr - 0 (list 1 2 3))")
        result = seval(expr, env)
        assert result == 2

    def test_for_each_returns_nil(self):
        env = make_global_env()
        expr = read_one("(for-each (lambda (x) x) (list 1 2 3))")
        result = seval(expr, env)
        assert result is NIL

    def test_apply(self):
        env = make_global_env()
        expr = read_one("(apply + (list 1 2 3))")
        result = seval(expr, env)
        assert result == 6

    def test_apply_non_list(self):
        env = make_global_env()
        expr = read_one("(apply + 42)")
        with pytest.raises(EvalError, match="apply: second argument must be a list"):
            seval(expr, env)


class TestStringOperations:
    """Tests for string operation builtins."""

    def test_string_append(self):
        env = make_global_env()
        expr = read_one('(string-append "hello" " " "world")')
        result = seval(expr, env)
        assert result == "hello world"

    def test_string_append_empty(self):
        env = make_global_env()
        expr = read_one("(string-append)")
        result = seval(expr, env)
        assert result == ""

    def test_string_append_non_string(self):
        env = make_global_env()
        expr = read_one('(string-append "hello" 42)')
        with pytest.raises(EvalError, match="string-append: all arguments must be strings"):
            seval(expr, env)

    def test_string_length(self):
        env = make_global_env()
        expr = read_one('(string-length "hello")')
        result = seval(expr, env)
        assert result == 5

    def test_string_length_empty(self):
        env = make_global_env()
        expr = read_one('(string-length "")')
        result = seval(expr, env)
        assert result == 0

    def test_string_length_non_string(self):
        env = make_global_env()
        expr = read_one("(string-length 42)")
        with pytest.raises(EvalError, match="string-length: argument must be a string"):
            seval(expr, env)

    def test_substring(self):
        env = make_global_env()
        expr = read_one('(substring "hello" 1 4)')
        result = seval(expr, env)
        assert result == "ell"

    def test_substring_full(self):
        env = make_global_env()
        expr = read_one('(substring "hello" 0 5)')
        result = seval(expr, env)
        assert result == "hello"

    def test_string_to_symbol(self):
        env = make_global_env()
        expr = read_one('(string->symbol "hello")')
        result = seval(expr, env)
        assert isinstance(result, Symbol)
        assert str(result) == "hello"

    def test_symbol_to_string(self):
        env = make_global_env()
        expr = read_one("(symbol->string 'hello)")
        result = seval(expr, env)
        assert result == "hello"
        assert isinstance(result, str)
        assert not isinstance(result, Symbol)

    def test_number_to_string_int(self):
        env = make_global_env()
        expr = read_one("(number->string 42)")
        result = seval(expr, env)
        assert result == "42"

    def test_number_to_string_float(self):
        env = make_global_env()
        expr = read_one("(number->string 3.14)")
        result = seval(expr, env)
        assert result == "3.14"

    def test_string_to_number_int(self):
        env = make_global_env()
        expr = read_one('(string->number "42")')
        result = seval(expr, env)
        assert result == 42

    def test_string_to_number_float(self):
        env = make_global_env()
        expr = read_one('(string->number "3.14")')
        result = seval(expr, env)
        assert result == 3.14

    def test_string_to_number_invalid(self):
        env = make_global_env()
        expr = read_one('(string->number "not a number")')
        result = seval(expr, env)
        assert result is False


class TestIO:
    """Tests for I/O builtins."""

    def test_error_raises(self):
        env = make_global_env()
        expr = read_one('(error "test error")')
        with pytest.raises(EvalError, match="test error"):
            seval(expr, env)

    def test_newline_returns_nil(self):
        env = make_global_env()
        expr = read_one("(newline)")
        result = seval(expr, env)
        assert result is NIL


class TestEdgeCases:
    """Edge case and integration tests."""

    def test_division_by_zero_still_works(self):
        """Ensure division by zero error is still caught after refactoring."""
        expr = read_one("(/ 10 0)")
        env = make_global_env()
        with pytest.raises(EvalError, match="division by zero"):
            seval(expr, env)

    def test_subtraction_zero_args(self):
        """Subtraction with no args should raise error."""
        expr = read_one("(-)")
        env = make_global_env()
        with pytest.raises(EvalError, match="- requires at least 1 argument"):
            seval(expr, env)

    def test_car_of_empty_list(self):
        """car of empty list should raise error."""
        expr = read_one("(car nil)")
        env = make_global_env()
        with pytest.raises(EvalError, match="empty list has no car"):
            seval(expr, env)

    def test_complex_nested_operations(self):
        """Test complex nested operations using multiple builtins."""
        env = make_global_env()
        result = eval_source(
            """
            (define double (lambda (x) (* x 2)))
            (map double (filter (lambda (x) (> x 0)) (list -1 2 -3 4)))
            """,
            env
        )
        assert list(result) == [4, 8]
