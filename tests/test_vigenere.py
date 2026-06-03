"""Tests for the Vigenère cipher example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys


@pytest.fixture(scope="module")
def vigenere_env_and_output():
    """Load the vigenere.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "vigenere.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestVigenere:
    """Tests for the Vigenère cipher example."""

    def test_example_output(self, vigenere_env_and_output):
        """Test that the example file produces the correct demo output."""
        env, demo_output = vigenere_env_and_output

        expected_lines = [
            "RIJVS",
            "lxfopvefrnhr"
        ]
        output_lines = demo_output.strip().split('\n')
        assert output_lines == expected_lines

    def test_hello_key_encrypt(self, vigenere_env_and_output):
        """Test HELLO with KEY produces RIJVS."""
        env, _ = vigenere_env_and_output
        result = eval_source('(vigenere-encrypt "HELLO" "KEY")', env)
        assert result == "RIJVS"

    def test_hello_key_decrypt(self, vigenere_env_and_output):
        """Test decryption of RIJVS with KEY produces HELLO."""
        env, _ = vigenere_env_and_output
        result = eval_source('(vigenere-decrypt "RIJVS" "KEY")', env)
        assert result == "HELLO"

    def test_canonical_encrypt(self, vigenere_env_and_output):
        """Test the canonical Vigenère example: attackatdawn with lemon."""
        env, _ = vigenere_env_and_output
        result = eval_source('(vigenere-encrypt "attackatdawn" "lemon")', env)
        assert result == "lxfopvefrnhr"

    def test_canonical_decrypt(self, vigenere_env_and_output):
        """Test decryption of the canonical example."""
        env, _ = vigenere_env_and_output
        result = eval_source('(vigenere-decrypt "lxfopvefrnhr" "lemon")', env)
        assert result == "attackatdawn"

    def test_key_all_a_no_op(self, vigenere_env_and_output):
        """Test that key of all 'a' leaves letters unchanged."""
        env, _ = vigenere_env_and_output
        result = eval_source('(vigenere-encrypt "Hello" "aaaaa")', env)
        assert result == "Hello"

    def test_key_all_a_uppercase_no_op(self, vigenere_env_and_output):
        """Test that key of all 'A' leaves letters unchanged."""
        env, _ = vigenere_env_and_output
        result = eval_source('(vigenere-encrypt "Hello" "AAAAA")', env)
        assert result == "Hello"

    def test_key_cycles_correctly(self, vigenere_env_and_output):
        """Test that key cycles over the text correctly."""
        env, _ = vigenere_env_and_output
        # "ab" with key "xy" should cycle: a+x, b+y, a+x, b+y
        # a (0) + x (23) = x, b (1) + y (24) = z, c (2) + x (23) = z, d (3) + y (24) = b
        result = eval_source('(vigenere-encrypt "abcd" "xy")', env)
        assert result == "xzzb"

    def test_mixed_case_spaces_punctuation_round_trip(self, vigenere_env_and_output):
        """Test round-trip with mixed case, spaces, and punctuation."""
        env, _ = vigenere_env_and_output
        original = "Hello, World!"
        key = "secret"
        encrypted = eval_source(f'(vigenere-encrypt "{original}" "{key}")', env)
        decrypted = eval_source(f'(vigenere-decrypt "{encrypted}" "{key}")', env)
        assert decrypted == original

    def test_attack_at_dawn_mixed_case_round_trip(self, vigenere_env_and_output):
        """Test round-trip with 'Attack at Dawn!' using key 'LEMON'."""
        env, _ = vigenere_env_and_output
        original = "Attack at Dawn!"
        key = "LEMON"
        encrypted = eval_source(f'(vigenere-encrypt "{original}" "{key}")', env)
        decrypted = eval_source(f'(vigenere-decrypt "{encrypted}" "{key}")', env)
        assert decrypted == original

    def test_non_letters_dont_consume_key(self, vigenere_env_and_output):
        """Test that non-alphabetic characters don't consume the key."""
        env, _ = vigenere_env_and_output
        # Encrypt "a b" with key "x" should be same as "ab" with key "x"
        # (the space doesn't consume the key, so both use key position 0)
        result1 = eval_source('(vigenere-encrypt "ab" "xy")', env)
        result2 = eval_source('(vigenere-encrypt "a b" "xy")', env)
        # result1 should be "xz" (a+x=x, b+y=z)
        # result2 should be "x z" (a+x=x, space unchanged, b+y=z using key[1])
        assert result1 == "xz"
        assert result2 == "x z"

    def test_numbers_and_punctuation_preserved(self, vigenere_env_and_output):
        """Test that numbers, spaces, and punctuation are preserved unchanged."""
        env, _ = vigenere_env_and_output
        result = eval_source('(vigenere-encrypt "Test123!@#" "abc")', env)
        # Only letters shift: T->T(0), e->e(1), s->t(2), t->v(0)
        # Numbers and punctuation preserved
        # T(65) + a(0) = T, e(101) + b(1) = f, s(115) + c(2) = u, t(116) + a(0) = t
        assert result == "Tfut123!@#"
