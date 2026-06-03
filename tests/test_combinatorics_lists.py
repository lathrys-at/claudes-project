"""Tests for list combinatorics functions: permutations and power-set."""
import pytest
from pebble.evaluator import make_global_env, seval, EvalError
from pebble.reader import read_one
from pebble.types import PebbleList, NIL


class TestPermutations:
    """Tests for the permutations function."""

    def test_permutations_empty_list(self):
        """(permutations nil) should return (()) - a list containing one empty list."""
        expr = read_one("(permutations nil)")
        env = make_global_env()
        result = seval(expr, env)
        # Result should be a list containing the empty list
        assert isinstance(result, PebbleList)
        assert len(result) == 1
        assert isinstance(result[0], PebbleList)
        assert len(result[0]) == 0

    def test_permutations_single_element(self):
        """(permutations (list 1)) should return ((1))."""
        expr = read_one("(permutations (list 1))")
        env = make_global_env()
        result = seval(expr, env)
        # Result should be a list with one permutation: (1)
        assert isinstance(result, PebbleList)
        assert len(result) == 1
        assert isinstance(result[0], PebbleList)
        assert len(result[0]) == 1
        assert result[0][0] == 1

    def test_permutations_two_elements_length(self):
        """(length (permutations (list 1 2))) should return 2."""
        expr = read_one("(length (permutations (list 1 2)))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 2

    def test_permutations_two_elements_contains(self):
        """(permutations (list 1 2)) should contain both (1 2) and (2 1)."""
        expr = read_one("(permutations (list 1 2))")
        env = make_global_env()
        result = seval(expr, env)
        assert isinstance(result, PebbleList)

        # Check that the result contains (list 1 2)
        contains_1_2 = any(
            tuple(perm) == (1, 2)
            for perm in result
            if isinstance(perm, PebbleList) and len(perm) == 2
        )
        assert contains_1_2, "Should contain permutation (1 2)"

        # Check that the result contains (list 2 1)
        contains_2_1 = any(
            tuple(perm) == (2, 1)
            for perm in result
            if isinstance(perm, PebbleList) and len(perm) == 2
        )
        assert contains_2_1, "Should contain permutation (2 1)"

    def test_permutations_three_elements_length(self):
        """(length (permutations (list 1 2 3))) should return 6."""
        expr = read_one("(length (permutations (list 1 2 3)))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 6

    def test_permutations_three_elements_contains(self):
        """(permutations (list 1 2 3)) should contain specific permutations."""
        expr = read_one("(permutations (list 1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert isinstance(result, PebbleList)

        # Check for (1 2 3)
        contains_1_2_3 = any(
            tuple(perm) == (1, 2, 3)
            for perm in result
            if isinstance(perm, PebbleList)
        )
        assert contains_1_2_3, "Should contain (1 2 3)"

        # Check for (3 2 1)
        contains_3_2_1 = any(
            tuple(perm) == (3, 2, 1)
            for perm in result
            if isinstance(perm, PebbleList)
        )
        assert contains_3_2_1, "Should contain (3 2 1)"

        # Check for (2 1 3)
        contains_2_1_3 = any(
            tuple(perm) == (2, 1, 3)
            for perm in result
            if isinstance(perm, PebbleList)
        )
        assert contains_2_1_3, "Should contain (2 1 3)"

    def test_permutations_four_elements_length(self):
        """(length (permutations (list 1 2 3 4))) should return 24."""
        expr = read_one("(length (permutations (list 1 2 3 4)))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 24


class TestPowerSet:
    """Tests for the power-set function."""

    def test_power_set_empty_list(self):
        """(power-set nil) should return (()) - a list containing one empty list."""
        expr = read_one("(power-set nil)")
        env = make_global_env()
        result = seval(expr, env)
        # Result should be a list containing the empty list
        assert isinstance(result, PebbleList)
        assert len(result) == 1
        assert isinstance(result[0], PebbleList)
        assert len(result[0]) == 0

    def test_power_set_single_element_length(self):
        """(length (power-set (list 1))) should return 2."""
        expr = read_one("(length (power-set (list 1)))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 2

    def test_power_set_single_element_contains(self):
        """(power-set (list 1)) should contain nil and (list 1)."""
        expr = read_one("(power-set (list 1))")
        env = make_global_env()
        result = seval(expr, env)
        assert isinstance(result, PebbleList)

        # Check for empty subset
        contains_empty = any(
            isinstance(subset, PebbleList) and len(subset) == 0
            for subset in result
        )
        assert contains_empty, "Should contain the empty subset"

        # Check for {1}
        contains_one = any(
            isinstance(subset, PebbleList) and tuple(subset) == (1,)
            for subset in result
        )
        assert contains_one, "Should contain {1}"

    def test_power_set_two_elements_length(self):
        """(length (power-set (list 1 2))) should return 4."""
        expr = read_one("(length (power-set (list 1 2)))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 4

    def test_power_set_two_elements_contains(self):
        """(power-set (list 1 2)) should contain nil, {1}, {2}, and {1, 2}."""
        expr = read_one("(power-set (list 1 2))")
        env = make_global_env()
        result = seval(expr, env)
        assert isinstance(result, PebbleList)

        # Check for empty subset
        contains_empty = any(
            isinstance(subset, PebbleList) and len(subset) == 0
            for subset in result
        )
        assert contains_empty, "Should contain the empty subset"

        # Check for {1}
        contains_one = any(
            isinstance(subset, PebbleList) and tuple(subset) == (1,)
            for subset in result
        )
        assert contains_one, "Should contain {1}"

        # Check for {2}
        contains_two = any(
            isinstance(subset, PebbleList) and tuple(subset) == (2,)
            for subset in result
        )
        assert contains_two, "Should contain {2}"

        # Check for {1, 2}
        contains_one_two = any(
            isinstance(subset, PebbleList) and tuple(subset) == (1, 2)
            for subset in result
        )
        assert contains_one_two, "Should contain {1, 2}"

    def test_power_set_three_elements_length(self):
        """(length (power-set (list 1 2 3))) should return 8."""
        expr = read_one("(length (power-set (list 1 2 3)))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 8

    def test_power_set_three_elements_contains(self):
        """(power-set (list 1 2 3)) should contain nil and {1, 2, 3}."""
        expr = read_one("(power-set (list 1 2 3))")
        env = make_global_env()
        result = seval(expr, env)
        assert isinstance(result, PebbleList)

        # Check for empty subset
        contains_empty = any(
            isinstance(subset, PebbleList) and len(subset) == 0
            for subset in result
        )
        assert contains_empty, "Should contain the empty subset"

        # Check for {1, 2, 3}
        contains_one_two_three = any(
            isinstance(subset, PebbleList) and tuple(subset) == (1, 2, 3)
            for subset in result
        )
        assert contains_one_two_three, "Should contain {1, 2, 3}"

    def test_power_set_five_elements_length(self):
        """(length (power-set (list 1 2 3 4 5))) should return 32."""
        expr = read_one("(length (power-set (list 1 2 3 4 5)))")
        env = make_global_env()
        result = seval(expr, env)
        assert result == 32
