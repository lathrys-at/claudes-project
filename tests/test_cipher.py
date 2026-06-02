"""Tests for the Caesar cipher / ROT13 example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


@pytest.fixture(scope="module")
def cipher_env_and_output():
    """Load the cipher.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "cipher.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestCipher:
    """Tests for the Caesar cipher / ROT13 example."""

    def test_example_output(self, cipher_env_and_output):
        """Test that the example file produces the correct demo output."""
        env, demo_output = cipher_env_and_output

        expected_lines = [
            "Khoor, Zruog!",
            "Uryyb"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_caesar_encrypt_simple(self, cipher_env_and_output):
        """Test caesar-encrypt with simple lowercase: 'abc' + 1 = 'bcd'."""
        env, _ = cipher_env_and_output

        result = eval_source('(caesar-encrypt "abc" 1)', env)
        assert result == "bcd"

    def test_caesar_encrypt_wrap(self, cipher_env_and_output):
        """Test caesar-encrypt wraps around: 'xyz' + 3 = 'abc'."""
        env, _ = cipher_env_and_output

        result = eval_source('(caesar-encrypt "xyz" 3)', env)
        assert result == "abc"

    def test_caesar_encrypt_case_preserved(self, cipher_env_and_output):
        """Test caesar-encrypt preserves case: 'Hello, World!' + 3 = 'Khoor, Zruog!'."""
        env, _ = cipher_env_and_output

        result = eval_source('(caesar-encrypt "Hello, World!" 3)', env)
        assert result == "Khoor, Zruog!"

    def test_caesar_encrypt_nonletters_unchanged(self, cipher_env_and_output):
        """Test caesar-encrypt leaves non-letters unchanged."""
        env, _ = cipher_env_and_output

        # Space, comma, exclamation should remain
        result = eval_source('(caesar-encrypt "Hello, World!" 3)', env)
        assert ", " in result
        assert "!" in result

    def test_caesar_decrypt_basic(self, cipher_env_and_output):
        """Test caesar-decrypt reverses encryption: decrypt(encrypt(x)) = x."""
        env, _ = cipher_env_and_output

        result = eval_source('(caesar-decrypt "Khoor, Zruog!" 3)', env)
        assert result == "Hello, World!"

    def test_caesar_roundtrip(self, cipher_env_and_output):
        """Test that decrypt(encrypt(x, shift), shift) = x."""
        env, _ = cipher_env_and_output

        result = eval_source('(caesar-decrypt (caesar-encrypt "Secret Message" 5) 5)', env)
        assert result == "Secret Message"

    def test_rot13_basic(self, cipher_env_and_output):
        """Test rot13: 'Hello' -> 'Uryyb'."""
        env, _ = cipher_env_and_output

        result = eval_source('(rot13 "Hello")', env)
        assert result == "Uryyb"

    def test_rot13_self_inverse(self, cipher_env_and_output):
        """Test rot13 is self-inverse: rot13(rot13(x)) = x."""
        env, _ = cipher_env_and_output

        result = eval_source('(rot13 (rot13 "Hello, World!"))', env)
        assert result == "Hello, World!"

    def test_rot13_full_alphabet(self, cipher_env_and_output):
        """Test rot13 on full lowercase alphabet."""
        env, _ = cipher_env_and_output

        result = eval_source('(rot13 "abcdefghijklmnopqrstuvwxyz")', env)
        assert result == "nopqrstuvwxyzabcdefghijklm"

    def test_caesar_encrypt_shift_zero(self, cipher_env_and_output):
        """Test caesar-encrypt with shift 0 leaves text unchanged."""
        env, _ = cipher_env_and_output

        result = eval_source('(caesar-encrypt "Hello" 0)', env)
        assert result == "Hello"

    def test_caesar_encrypt_shift_twentysix(self, cipher_env_and_output):
        """Test caesar-encrypt with shift 26 leaves text unchanged (full rotation)."""
        env, _ = cipher_env_and_output

        result = eval_source('(caesar-encrypt "Hello" 26)', env)
        assert result == "Hello"

    def test_caesar_encrypt_empty_string(self, cipher_env_and_output):
        """Test caesar-encrypt on empty string returns empty string."""
        env, _ = cipher_env_and_output

        result = eval_source('(caesar-encrypt "" 5)', env)
        assert result == ""
