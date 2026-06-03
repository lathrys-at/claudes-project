"""Tests for numeric helper functions: clamp, sign, lerp."""

import pytest
from pebble.evaluator import make_global_env, eval_source


def eval_pebble(source):
    """Helper to evaluate Pebble source and return result."""
    env = make_global_env()
    return eval_source(source, env)


class TestClamp:
    """Tests for clamp function."""

    def test_clamp_within_range(self):
        """clamp returns x when x is within [lo, hi]."""
        assert eval_pebble("(clamp 5 0 10)") == 5
        assert eval_pebble("(clamp 7 0 10)") == 7
        assert eval_pebble("(clamp 0 0 10)") == 0
        assert eval_pebble("(clamp 10 0 10)") == 10

    def test_clamp_below_range(self):
        """clamp returns lo when x < lo."""
        assert eval_pebble("(clamp -3 0 10)") == 0
        assert eval_pebble("(clamp -1 -5 5)") == -1
        assert eval_pebble("(clamp -100 0 10)") == 0

    def test_clamp_above_range(self):
        """clamp returns hi when x > hi."""
        assert eval_pebble("(clamp 15 0 10)") == 10
        assert eval_pebble("(clamp 7 0 5)") == 5
        assert eval_pebble("(clamp 100 0 10)") == 10

    def test_clamp_equal_bounds(self):
        """clamp with lo = hi."""
        assert eval_pebble("(clamp 5 5 5)") == 5
        assert eval_pebble("(clamp 3 5 5)") == 5
        assert eval_pebble("(clamp 7 5 5)") == 5

    def test_clamp_negative_range(self):
        """clamp with negative lo and hi."""
        assert eval_pebble("(clamp -3 -10 -1)") == -3
        assert eval_pebble("(clamp -15 -10 -1)") == -10
        assert eval_pebble("(clamp 0 -10 -1)") == -1

    def test_clamp_floats(self):
        """clamp works with floating point numbers."""
        assert eval_pebble("(clamp 2.5 0.0 5.0)") == 2.5
        assert eval_pebble("(clamp -0.5 0.0 5.0)") == 0.0
        assert eval_pebble("(clamp 6.5 0.0 5.0)") == 5.0


class TestSign:
    """Tests for sign function."""

    def test_sign_negative(self):
        """sign returns -1 for negative numbers."""
        assert eval_pebble("(sign -7)") == -1
        assert eval_pebble("(sign -1)") == -1
        assert eval_pebble("(sign -100)") == -1

    def test_sign_positive(self):
        """sign returns 1 for positive numbers."""
        assert eval_pebble("(sign 42)") == 1
        assert eval_pebble("(sign 1)") == 1
        assert eval_pebble("(sign 100)") == 1

    def test_sign_zero(self):
        """sign returns 0 for zero."""
        assert eval_pebble("(sign 0)") == 0

    def test_sign_floats_negative(self):
        """sign returns -1 for negative floats."""
        assert eval_pebble("(sign -0.5)") == -1
        assert eval_pebble("(sign -3.7)") == -1

    def test_sign_floats_positive(self):
        """sign returns 1 for positive floats."""
        assert eval_pebble("(sign 3.5)") == 1
        assert eval_pebble("(sign 0.1)") == 1

    def test_sign_float_zero(self):
        """sign returns 0 for zero as float."""
        assert eval_pebble("(sign 0.0)") == 0


class TestLerp:
    """Tests for lerp (linear interpolation) function."""

    def test_lerp_at_start(self):
        """lerp returns a when t=0."""
        assert eval_pebble("(lerp 0 10 0)") == 0
        assert eval_pebble("(lerp 5 15 0)") == 5
        assert eval_pebble("(lerp -10 10 0)") == -10

    def test_lerp_at_end(self):
        """lerp returns b when t=1."""
        assert eval_pebble("(lerp 0 10 1)") == 10
        assert eval_pebble("(lerp 5 15 1)") == 15
        assert eval_pebble("(lerp -10 10 1)") == 10

    def test_lerp_midpoint(self):
        """lerp returns midpoint when t=0.5."""
        result = eval_pebble("(lerp 0 10 0.5)")
        assert result == 5 or result == 5.0

        result = eval_pebble("(lerp 10 20 0.5)")
        assert result == 15 or result == 15.0

        result = eval_pebble("(lerp -10 10 0.5)")
        assert result == 0 or result == 0.0

        result = eval_pebble("(lerp 100 200 0.5)")
        assert result == 150 or result == 150.0

    def test_lerp_quarter_point(self):
        """lerp at t=0.25."""
        result = eval_pebble("(lerp 10 20 0.25)")
        assert result == 12.5 or result == 12.5

    def test_lerp_three_quarter_point(self):
        """lerp at t=0.75."""
        result = eval_pebble("(lerp 0 100 0.75)")
        assert result == 75 or result == 75.0

    def test_lerp_with_negative_numbers(self):
        """lerp with negative start and end."""
        result = eval_pebble("(lerp -20 -10 0.5)")
        assert result == -15 or result == -15.0

    def test_lerp_extrapolation(self):
        """lerp can extrapolate beyond [0,1] range."""
        result = eval_pebble("(lerp 0 10 2)")
        assert result == 20 or result == 20.0

        result = eval_pebble("(lerp 0 10 -1)")
        assert result == -10 or result == -10.0

    def test_lerp_floats(self):
        """lerp with floating point inputs."""
        result = eval_pebble("(lerp 0.0 1.0 0.5)")
        assert abs(result - 0.5) < 1e-10 or result == 0.5
