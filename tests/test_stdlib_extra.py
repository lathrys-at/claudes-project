"""Tests for extended standard library functions."""
import pytest
from pebble.evaluator import eval_source, make_global_env, EvalError
from pebble.types import PebbleList, NIL


class TestSort:
    """Tests for the sort function."""

    def test_sort_numbers_ascending(self):
        env = make_global_env()
        result = eval_source("(sort (list 3 1 4 1 5 9 2 6))", env)
        assert list(result) == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_sort_empty_list(self):
        env = make_global_env()
        result = eval_source("(sort (list))", env)
        assert result == NIL

    def test_sort_single_element(self):
        env = make_global_env()
        result = eval_source("(sort (list 42))", env)
        assert list(result) == [42]

    def test_sort_with_duplicates(self):
        env = make_global_env()
        result = eval_source("(sort (list 5 5 1 1 3 3))", env)
        assert list(result) == [1, 1, 3, 3, 5, 5]

    def test_sort_with_negative_numbers(self):
        env = make_global_env()
        result = eval_source("(sort (list 3 -1 0 -5 2))", env)
        assert list(result) == [-5, -1, 0, 2, 3]

    def test_sort_immutability(self):
        env = make_global_env()
        eval_source("""
            (define original (list 3 1 2))
            (define sorted (sort original))
        """, env)
        original = eval_source("original", env)
        assert list(original) == [3, 1, 2]

    def test_sort_strings_lexicographically(self):
        env = make_global_env()
        result = eval_source('(sort (list "zebra" "apple" "banana"))', env)
        assert list(result) == ["apple", "banana", "zebra"]

    def test_sort_already_sorted(self):
        env = make_global_env()
        result = eval_source("(sort (list 1 2 3 4 5))", env)
        assert list(result) == [1, 2, 3, 4, 5]

    def test_sort_reverse_sorted(self):
        env = make_global_env()
        result = eval_source("(sort (list 5 4 3 2 1))", env)
        assert list(result) == [1, 2, 3, 4, 5]


class TestSortWith:
    """Tests for the sort-with function."""

    def test_sort_with_descending_order(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (> a b)) (list 3 1 4 1 5 9 2 6))
        """, env)
        assert list(result) == [9, 6, 5, 4, 3, 2, 1, 1]

    def test_sort_with_ascending_order(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (< a b)) (list 3 1 4 1 5 9 2 6))
        """, env)
        assert list(result) == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_sort_with_absolute_value(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (< (abs a) (abs b))) (list 5 -3 4 -1 2))
        """, env)
        # Sorted by absolute value: -1, 2, -3, 4, 5
        assert list(result) == [-1, 2, -3, 4, 5]

    def test_sort_with_empty_list(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (< a b)) (list))
        """, env)
        assert result == NIL

    def test_sort_with_single_element(self):
        env = make_global_env()
        result = eval_source("""
            (sort-with (lambda (a b) (< a b)) (list 42))
        """, env)
        assert list(result) == [42]

    def test_sort_stability(self):
        """Test that sort is stable: equal elements retain original order."""
        env = make_global_env()
        # Create a list of pairs (lists), sort by first element
        result = eval_source("""
            (define data (list (list 2 "a") (list 1 "b") (list 2 "c") (list 1 "d")))
            (sort-with (lambda (x y) (< (car x) (car y))) data)
        """, env)
        result_list = [list(x) for x in result]
        # Should be: (1 "b"), (1 "d"), (2 "a"), (2 "c")
        # The pairs with equal first elements should keep their original relative order
        assert result_list == [[1, "b"], [1, "d"], [2, "a"], [2, "c"]]

    def test_sort_large_list_ascending(self):
        """Test that sort handles a large list efficiently without stack overflow."""
        env = make_global_env()
        # Create a reverse-sorted list of 1500 elements
        result = eval_source("""
            (define reverse-sorted (reverse (range 1500)))
            (sort reverse-sorted)
        """, env)
        expected = list(range(1500))
        assert list(result) == expected

    def test_sort_large_list_already_sorted(self):
        """Test that sort handles an already-sorted large list efficiently."""
        env = make_global_env()
        # Create an ascending list of 1500 elements
        result = eval_source("""
            (define ascending (range 1500))
            (sort ascending)
        """, env)
        expected = list(range(1500))
        assert list(result) == expected

    def test_sort_large_list_with_sort_with(self):
        """Test that sort-with handles a large list efficiently."""
        env = make_global_env()
        # Create a forward-sorted list and sort it descending
        result = eval_source("""
            (sort-with (lambda (a b) (> a b)) (range 1500))
        """, env)
        expected = list(range(1499, -1, -1))
        assert list(result) == expected


class TestAssoc:
    """Tests for the assoc function."""

    def test_assoc_found(self):
        env = make_global_env()
        result = eval_source("""
            (assoc "x" (list (list "x" 1) (list "y" 2)))
        """, env)
        assert list(result) == ["x", 1]

    def test_assoc_not_found(self):
        env = make_global_env()
        result = eval_source("""
            (assoc "z" (list (list "x" 1) (list "y" 2)))
        """, env)
        assert result is False

    def test_assoc_empty_list(self):
        env = make_global_env()
        result = eval_source("""
            (assoc "x" (list))
        """, env)
        assert result is False

    def test_assoc_first_of_duplicates(self):
        env = make_global_env()
        result = eval_source("""
            (assoc "x" (list (list "x" 1) (list "x" 2)))
        """, env)
        # Should return first match
        assert list(result) == ["x", 1]

    def test_assoc_with_numeric_keys(self):
        env = make_global_env()
        result = eval_source("""
            (assoc 42 (list (list 1 "a") (list 42 "b") (list 99 "c")))
        """, env)
        assert list(result) == [42, "b"]


class TestContains:
    """Tests for the contains? function."""

    def test_contains_present(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 3 4) 3)", env)
        assert result is True

    def test_contains_not_present(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 3 4) 5)", env)
        assert result is False

    def test_contains_empty_list(self):
        env = make_global_env()
        result = eval_source("(contains? (list) 1)", env)
        assert result is False

    def test_contains_first_element(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 3) 1)", env)
        assert result is True

    def test_contains_last_element(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 3) 3)", env)
        assert result is True

    def test_contains_with_strings(self):
        env = make_global_env()
        result = eval_source('(contains? (list "a" "b" "c") "b")', env)
        assert result is True

    def test_contains_with_duplicates(self):
        env = make_global_env()
        result = eval_source("(contains? (list 1 2 1 3) 1)", env)
        assert result is True


class TestIndexOf:
    """Tests for the index-of function."""

    def test_index_of_found_first(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 3 4) 3)", env)
        assert result == 2

    def test_index_of_found_zero(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 3 4) 1)", env)
        assert result == 0

    def test_index_of_not_found(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 3 4) 5)", env)
        assert result == -1

    def test_index_of_empty_list(self):
        env = make_global_env()
        result = eval_source("(index-of (list) 1)", env)
        assert result == -1

    def test_index_of_first_of_duplicates(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 1 3) 1)", env)
        # Should return first occurrence
        assert result == 0

    def test_index_of_with_strings(self):
        env = make_global_env()
        result = eval_source('(index-of (list "a" "b" "c") "b")', env)
        assert result == 1

    def test_index_of_last_element(self):
        env = make_global_env()
        result = eval_source("(index-of (list 1 2 3 4 5) 5)", env)
        assert result == 4


class TestMaximum:
    """Tests for the maximum function."""

    def test_maximum_basic(self):
        env = make_global_env()
        result = eval_source("(maximum (list 1 5 3 2 4))", env)
        assert result == 5

    def test_maximum_single_element(self):
        env = make_global_env()
        result = eval_source("(maximum (list 42))", env)
        assert result == 42

    def test_maximum_with_negatives(self):
        env = make_global_env()
        result = eval_source("(maximum (list -1 -5 -3))", env)
        assert result == -1

    def test_maximum_with_duplicates(self):
        env = make_global_env()
        result = eval_source("(maximum (list 5 5 5))", env)
        assert result == 5

    def test_maximum_empty_list_raises_error(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="maximum: empty list"):
            eval_source("(maximum (list))", env)

    def test_maximum_with_floats(self):
        env = make_global_env()
        result = eval_source("(maximum (list 1.5 2.7 0.3))", env)
        assert result == 2.7


class TestMinimum:
    """Tests for the minimum function."""

    def test_minimum_basic(self):
        env = make_global_env()
        result = eval_source("(minimum (list 5 1 3 2 4))", env)
        assert result == 1

    def test_minimum_single_element(self):
        env = make_global_env()
        result = eval_source("(minimum (list 42))", env)
        assert result == 42

    def test_minimum_with_negatives(self):
        env = make_global_env()
        result = eval_source("(minimum (list -1 -5 -3))", env)
        assert result == -5

    def test_minimum_with_duplicates(self):
        env = make_global_env()
        result = eval_source("(minimum (list 5 5 5))", env)
        assert result == 5

    def test_minimum_empty_list_raises_error(self):
        env = make_global_env()
        with pytest.raises(EvalError, match="minimum: empty list"):
            eval_source("(minimum (list))", env)

    def test_minimum_with_floats(self):
        env = make_global_env()
        result = eval_source("(minimum (list 1.5 2.7 0.3))", env)
        assert result == 0.3


class TestRepeat:
    """Tests for the repeat function."""

    def test_repeat_basic(self):
        env = make_global_env()
        result = eval_source("(repeat 42 3)", env)
        assert list(result) == [42, 42, 42]

    def test_repeat_zero(self):
        env = make_global_env()
        result = eval_source("(repeat 42 0)", env)
        assert result == NIL

    def test_repeat_one(self):
        env = make_global_env()
        result = eval_source("(repeat 42 1)", env)
        assert list(result) == [42]

    def test_repeat_string(self):
        env = make_global_env()
        result = eval_source('(repeat "x" 5)', env)
        assert list(result) == ["x", "x", "x", "x", "x"]

    def test_repeat_list(self):
        env = make_global_env()
        result = eval_source("(repeat (list 1 2) 2)", env)
        assert len(result) == 2
        assert list(result[0]) == [1, 2]
        assert list(result[1]) == [1, 2]

    def test_repeat_large_n(self):
        env = make_global_env()
        result = eval_source("(repeat 1 100)", env)
        assert len(result) == 100
        assert all(x == 1 for x in result)


class TestStringSplit:
    """Tests for the string-split function."""

    def test_string_split_basic(self):
        env = make_global_env()
        result = eval_source('(string-split "a,b,c" ",")', env)
        assert list(result) == ["a", "b", "c"]

    def test_string_split_consecutive_separators(self):
        env = make_global_env()
        result = eval_source('(string-split "a,,c" ",")', env)
        assert list(result) == ["a", "", "c"]

    def test_string_split_separator_not_present(self):
        env = make_global_env()
        result = eval_source('(string-split "abc" ",")', env)
        assert list(result) == ["abc"]

    def test_string_split_empty_string(self):
        env = make_global_env()
        result = eval_source('(string-split "" ",")', env)
        assert list(result) == [""]

    def test_string_split_leading_separator(self):
        env = make_global_env()
        result = eval_source('(string-split ",a" ",")', env)
        assert list(result) == ["", "a"]

    def test_string_split_trailing_separator(self):
        env = make_global_env()
        result = eval_source('(string-split "a," ",")', env)
        assert list(result) == ["a", ""]

    def test_string_split_multi_char_separator(self):
        env = make_global_env()
        result = eval_source('(string-split "a::b::c" "::")', env)
        assert list(result) == ["a", "b", "c"]

    def test_string_split_space_separator(self):
        env = make_global_env()
        result = eval_source('(string-split "hello world test" " ")', env)
        assert list(result) == ["hello", "world", "test"]

    def test_string_split_multi_char_consecutive(self):
        env = make_global_env()
        result = eval_source('(string-split "a::::b" "::")', env)
        assert list(result) == ["a", "", "b"]

    def test_string_split_only_separator(self):
        env = make_global_env()
        result = eval_source('(string-split "," ",")', env)
        assert list(result) == ["", ""]

    def test_string_split_multiple_consecutive_separators(self):
        env = make_global_env()
        result = eval_source('(string-split "a,,,b" ",")', env)
        assert list(result) == ["a", "", "", "b"]


class TestCaseMacro:
    """Tests for the case macro."""

    def test_case_numeric_dispatch(self):
        """Test case with numeric keys."""
        env = make_global_env()
        result = eval_source("""
            (case 2
              ((1) "one")
              ((2 3) "two-or-three")
              (else "other"))
        """, env)
        assert result == "two-or-three"

    def test_case_first_match(self):
        """Test that case returns the first matching clause."""
        env = make_global_env()
        result = eval_source("""
            (case 2
              ((1) "one")
              ((2) "first-two")
              ((2) "second-two"))
        """, env)
        assert result == "first-two"

    def test_case_string_dispatch(self):
        """Test case with string keys."""
        env = make_global_env()
        result = eval_source("""
            (case "hello"
              (("goodbye") "bye")
              (("hello") "hi")
              (else "unknown"))
        """, env)
        assert result == "hi"

    def test_case_no_match_no_else(self):
        """Test case when no clause matches and there is no else."""
        env = make_global_env()
        result = eval_source("""
            (case 5
              ((1 2 3) "small")
              ((4) "four"))
        """, env)
        assert result == NIL

    def test_case_else_fallthrough(self):
        """Test case else clause."""
        env = make_global_env()
        result = eval_source("""
            (case 100
              ((1 2) "small")
              ((10 20) "medium")
              (else "large"))
        """, env)
        assert result == "large"

    def test_case_key_evaluated_once(self):
        """Test that the key expression is evaluated exactly once."""
        env = make_global_env()
        result = eval_source("""
            (define counter 0)
            (define increment-and-return
              (lambda ()
                (begin
                  (set! counter (+ counter 1))
                  2)))
            (case (increment-and-return)
              ((1) "one")
              ((2) "two")
              (else "other"))
            counter
        """, env)
        # counter should be 1, meaning the key expr was evaluated exactly once
        assert result == 1

    def test_case_with_multiple_datums_in_clause(self):
        """Test case with multiple datums in a single clause."""
        env = make_global_env()
        result = eval_source("""
            (case "x"
              (("a" "b" "c") "abc")
              (("x" "y" "z") "xyz")
              (else "other"))
        """, env)
        assert result == "xyz"

    def test_case_empty_body_returns_nil(self):
        """Test case clause with empty body."""
        env = make_global_env()
        result = eval_source("""
            (case 2
              ((1) "one")
              ((2)))
        """, env)
        assert result == NIL

    def test_case_multiple_body_forms(self):
        """Test case with multiple body forms in a clause."""
        env = make_global_env()
        result = eval_source("""
            (define x 0)
            (case 2
              ((1) (set! x 1) "one")
              ((2) (set! x 2) (set! x (+ x 10)) "result")
              (else "other"))
            (list (list "result" "result") (list "x" x))
        """, env)
        assert list(result)[1][1] == 12

    def test_case_symbol_dispatch(self):
        """Test case with symbol keys."""
        env = make_global_env()
        result = eval_source("""
            (case 'b
              ((a) "first")
              ((b c) "second")
              (else "other"))
        """, env)
        assert result == "second"


class TestWhileMacro:
    """Tests for the while macro."""

    def test_while_basic_loop_accumulation(self):
        """Test basic while loop with accumulation."""
        env = make_global_env()
        result = eval_source("""
            (define i 0)
            (define sum 0)
            (while (< i 5)
              (set! sum (+ sum i))
              (set! i (+ i 1)))
            (list sum i)
        """, env)
        assert list(result) == [10, 5]

    def test_while_returns_nil(self):
        """Test that while returns nil."""
        env = make_global_env()
        result = eval_source("""
            (define i 0)
            (while (< i 3)
              (set! i (+ i 1)))
        """, env)
        assert result == NIL

    def test_while_condition_initially_false(self):
        """Test while when condition is initially false."""
        env = make_global_env()
        result = eval_source("""
            (define flag false)
            (while false
              (set! flag true))
            flag
        """, env)
        assert result is False

    def test_while_condition_initially_true(self):
        """Test while when condition is initially true."""
        env = make_global_env()
        result = eval_source("""
            (define i 0)
            (while (< i 1)
              (set! i (+ i 1)))
            i
        """, env)
        assert result == 1

    def test_while_countdown(self):
        """Test while with countdown."""
        env = make_global_env()
        result = eval_source("""
            (define count 10)
            (while (> count 0)
              (set! count (- count 1)))
            count
        """, env)
        assert result == 0

    def test_while_multiple_body_forms(self):
        """Test while with multiple body forms."""
        env = make_global_env()
        result = eval_source("""
            (define i 0)
            (define sum 0)
            (while (< i 3)
              (set! sum (+ sum 1))
              (set! sum (+ sum 10))
              (set! i (+ i 1)))
            sum
        """, env)
        # Each iteration: sum += 1, sum += 10 (adds 11 per iteration)
        # 3 iterations: 11 * 3 = 33
        assert result == 33

    def test_while_large_loop_no_stack_overflow(self):
        """Test that while with 20000 iterations does not overflow stack."""
        env = make_global_env()
        result = eval_source("""
            (define i 0)
            (define c 0)
            (while (< c 20000)
              (set! i (+ i 1))
              (set! c (+ c 1)))
            i
        """, env)
        assert result == 20000

    def test_while_string_mutation(self):
        """Test while with string concatenation."""
        env = make_global_env()
        result = eval_source("""
            (define s "")
            (define i 0)
            (while (< i 3)
              (set! s (string-append s "x"))
              (set! i (+ i 1)))
            s
        """, env)
        assert result == "xxx"


class TestDotimesMacro:
    """Tests for the dotimes macro."""

    def test_dotimes_basic_accumulation(self):
        """Test basic dotimes loop with accumulation."""
        env = make_global_env()
        result = eval_source("""
            (define total 0)
            (dotimes (i 5)
              (set! total (+ total i)))
            total
        """, env)
        assert result == 10

    def test_dotimes_returns_nil(self):
        """Test that dotimes returns nil."""
        env = make_global_env()
        result = eval_source("""
            (dotimes (i 3)
              (+ i 1))
        """, env)
        assert result == NIL

    def test_dotimes_zero_iterations(self):
        """Test dotimes with count 0."""
        env = make_global_env()
        result = eval_source("""
            (define flag false)
            (dotimes (i 0)
              (set! flag true))
            flag
        """, env)
        assert result is False

    def test_dotimes_single_iteration(self):
        """Test dotimes with count 1."""
        env = make_global_env()
        result = eval_source("""
            (define x 0)
            (dotimes (i 1)
              (set! x (+ x 10)))
            x
        """, env)
        assert result == 10

    def test_dotimes_correct_iteration_count(self):
        """Test that dotimes iterates correct number of times."""
        env = make_global_env()
        result = eval_source("""
            (define count 0)
            (dotimes (i 7)
              (set! count (+ count 1)))
            count
        """, env)
        assert result == 7

    def test_dotimes_var_binding(self):
        """Test that loop variable is correctly bound."""
        env = make_global_env()
        result = eval_source("""
            (define sum 0)
            (dotimes (i 4)
              (set! sum (+ sum i)))
            sum
        """, env)
        # 0 + 1 + 2 + 3 = 6
        assert result == 6

    def test_dotimes_multiple_body_forms(self):
        """Test dotimes with multiple body forms."""
        env = make_global_env()
        result = eval_source("""
            (define s "")
            (define c 0)
            (dotimes (i 3)
              (set! s (string-append s "x"))
              (set! c (+ c 1)))
            (list s c)
        """, env)
        assert list(result) == ["xxx", 3]

    def test_dotimes_negative_count(self):
        """Test dotimes with negative count."""
        env = make_global_env()
        result = eval_source("""
            (define flag false)
            (dotimes (i -5)
              (set! flag true))
            flag
        """, env)
        # Negative count should result in 0 iterations
        assert result is False

    def test_dotimes_var_not_in_scope_after(self):
        """Test that loop variable is scoped only to the loop body."""
        env = make_global_env()
        result = eval_source("""
            (define x 100)
            (dotimes (x 3)
              (+ x 1))
            x
        """, env)
        # x should still be 100 outside the loop
        assert result == 100

    def test_dotimes_large_count_no_stack_overflow(self):
        """Test that dotimes with 20000 iterations does not overflow stack."""
        env = make_global_env()
        result = eval_source("""
            (define c 0)
            (dotimes (i 20000)
              (set! c (+ c 1)))
            c
        """, env)
        assert result == 20000

    def test_dotimes_count_expr_evaluated_once(self):
        """Test that count expression is evaluated exactly once."""
        env = make_global_env()
        result = eval_source("""
            (define eval_count 0)
            (define get_count
              (lambda ()
                (begin
                  (set! eval_count (+ eval_count 1))
                  5)))
            (dotimes (i (get_count))
              (+ i 1))
            eval_count
        """, env)
        # get_count should be called exactly once
        assert result == 1
