"""Tests for the number-to-English-words converter example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


@pytest.fixture(scope="module")
def number_words_env_and_output():
    """Load the number_words.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "number_words.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestNumberWords:
    """Tests for the number-to-English-words converter."""

    def test_example_output(self, number_words_env_and_output):
        """Test that the example file produces the correct demo output."""
        env, demo_output = number_words_env_and_output

        expected_output = "two thousand twenty-four\n"
        assert demo_output == expected_output

    def test_zero(self, number_words_env_and_output):
        """Test zero."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 0)", env)
        assert result == "zero"

    def test_single_digit(self, number_words_env_and_output):
        """Test single digit: 7 -> 'seven'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 7)", env)
        assert result == "seven"

    def test_teens(self, number_words_env_and_output):
        """Test teens: 13 -> 'thirteen'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 13)", env)
        assert result == "thirteen"

    def test_twenty(self, number_words_env_and_output):
        """Test round tens: 20 -> 'twenty'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 20)", env)
        assert result == "twenty"

    def test_twenty_one_hyphenated(self, number_words_env_and_output):
        """Test hyphenated tens: 21 -> 'twenty-one'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 21)", env)
        assert result == "twenty-one"

    def test_forty_five_hyphenated(self, number_words_env_and_output):
        """Test hyphenated tens: 45 -> 'forty-five'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 45)", env)
        assert result == "forty-five"

    def test_one_hundred(self, number_words_env_and_output):
        """Test round hundreds: 100 -> 'one hundred'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 100)", env)
        assert result == "one hundred"

    def test_one_hundred_twenty_three(self, number_words_env_and_output):
        """Test hundreds with remainder: 123 -> 'one hundred twenty-three'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 123)", env)
        assert result == "one hundred twenty-three"

    def test_three_hundred_five(self, number_words_env_and_output):
        """Test hundreds with single digit remainder: 305 -> 'three hundred five'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 305)", env)
        assert result == "three hundred five"

    def test_one_thousand(self, number_words_env_and_output):
        """Test round thousands: 1000 -> 'one thousand'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 1000)", env)
        assert result == "one thousand"

    def test_two_thousand_twenty_four(self, number_words_env_and_output):
        """Test thousands with remainder: 2024 -> 'two thousand twenty-four'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 2024)", env)
        assert result == "two thousand twenty-four"

    def test_nine_thousand_nine_hundred_ninety_nine(self, number_words_env_and_output):
        """Test maximum value: 9999 -> 'nine thousand nine hundred ninety-nine'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 9999)", env)
        assert result == "nine thousand nine hundred ninety-nine"

    def test_five_thousand(self, number_words_env_and_output):
        """Test thousands without remainder: 5000 -> 'five thousand'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 5000)", env)
        assert result == "five thousand"

    def test_seven_thousand_forty_two(self, number_words_env_and_output):
        """Test thousands with small remainder: 7042 -> 'seven thousand forty-two'."""
        env, _ = number_words_env_and_output
        result = eval_source("(number->words 7042)", env)
        assert result == "seven thousand forty-two"

    def test_error_negative(self, number_words_env_and_output):
        """Test that negative numbers raise EvalError."""
        env, _ = number_words_env_and_output
        with pytest.raises(Exception) as exc_info:
            eval_source("(number->words -1)", env)
        assert "between 0 and 9999" in str(exc_info.value)

    def test_error_out_of_range(self, number_words_env_and_output):
        """Test that numbers >= 10000 raise EvalError."""
        env, _ = number_words_env_and_output
        with pytest.raises(Exception) as exc_info:
            eval_source("(number->words 10000)", env)
        assert "between 0 and 9999" in str(exc_info.value)

    def test_error_not_integer(self, number_words_env_and_output):
        """Test that non-integers raise EvalError."""
        env, _ = number_words_env_and_output
        with pytest.raises(Exception) as exc_info:
            eval_source("(number->words 3.14)", env)
        assert "integer" in str(exc_info.value)
