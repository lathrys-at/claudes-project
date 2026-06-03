"""Tests for Huffman coding example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleList
import io
import sys


@pytest.fixture(scope="module")
def huffman_env_and_output():
    """Load huffman.pebble once and capture its output."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "huffman.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestCharFrequencies:
    """Test char-frequencies function."""

    def test_char_frequencies_simple(self, huffman_env_and_output):
        """Test frequency counting on a simple string."""
        env, _ = huffman_env_and_output
        result = eval_source('(char-frequencies "aab")', env)
        # Should be a hash with "a" -> 2 and "b" -> 1
        assert eval_source('(hash-ref (char-frequencies "aab") "a")', env) == 2
        assert eval_source('(hash-ref (char-frequencies "aab") "b")', env) == 1

    def test_char_frequencies_empty(self, huffman_env_and_output):
        """Test frequency counting on empty string."""
        env, _ = huffman_env_and_output
        result = eval_source('(char-frequencies "")', env)
        # Should be an empty hash
        is_hash = eval_source('(hash? (char-frequencies ""))', env)
        assert is_hash
        keys = eval_source('(hash-keys (char-frequencies ""))', env)
        assert keys == PebbleList(())

    def test_char_frequencies_single(self, huffman_env_and_output):
        """Test frequency counting on single character."""
        env, _ = huffman_env_and_output
        result = eval_source('(char-frequencies "a")', env)
        assert eval_source('(hash-ref (char-frequencies "a") "a")', env) == 1

    def test_char_frequencies_all_distinct(self, huffman_env_and_output):
        """Test frequency counting on all-distinct characters."""
        env, _ = huffman_env_and_output
        result = eval_source('(char-frequencies "abc")', env)
        # Should have 3 distinct keys, each with count 1
        keys = eval_source('(hash-keys (char-frequencies "abc"))', env)
        assert len(keys) == 3
        assert eval_source('(hash-ref (char-frequencies "abc") "a")', env) == 1
        assert eval_source('(hash-ref (char-frequencies "abc") "b")', env) == 1
        assert eval_source('(hash-ref (char-frequencies "abc") "c")', env) == 1

    def test_char_frequencies_repeated(self, huffman_env_and_output):
        """Test frequency counting on highly repeated character."""
        env, _ = huffman_env_and_output
        result = eval_source('(char-frequencies "aaaa")', env)
        keys = eval_source('(hash-keys (char-frequencies "aaaa"))', env)
        assert len(keys) == 1
        assert eval_source('(hash-ref (char-frequencies "aaaa") "a")', env) == 4

    def test_char_frequencies_spaces(self, huffman_env_and_output):
        """Test frequency counting includes spaces."""
        env, _ = huffman_env_and_output
        result = eval_source('(char-frequencies "a b a")', env)
        assert eval_source('(hash-ref (char-frequencies "a b a") "a")', env) == 2
        assert eval_source('(hash-ref (char-frequencies "a b a") " ")', env) == 2
        assert eval_source('(hash-ref (char-frequencies "a b a") "b")', env) == 1


class TestHuffmanRoundTrip:
    """Test the central round-trip property."""

    def test_roundtrip_simple(self, huffman_env_and_output):
        """Test round-trip on simple string."""
        env, _ = huffman_env_and_output
        original = "hello"
        # Encode
        encoded = eval_source('(huffman-encode "hello")', env)
        # Extract tree and bits
        tree = eval_source('(car (huffman-encode "hello"))', env)
        bits = eval_source('(cadr (huffman-encode "hello"))', env)
        # Decode
        decoded = eval_source('(huffman-decode (car (huffman-encode "hello")) (cadr (huffman-encode "hello")))', env)
        assert decoded == original

    def test_roundtrip_repeated_chars(self, huffman_env_and_output):
        """Test round-trip on string with many repeated characters."""
        env, _ = huffman_env_and_output
        original = "aaaaaabbbc"
        decoded = eval_source('(huffman-decode (car (huffman-encode "aaaaaabbbc")) (cadr (huffman-encode "aaaaaabbbc")))', env)
        assert decoded == original

    def test_roundtrip_all_distinct(self, huffman_env_and_output):
        """Test round-trip on all-distinct characters."""
        env, _ = huffman_env_and_output
        original = "abcdef"
        decoded = eval_source('(huffman-decode (car (huffman-encode "abcdef")) (cadr (huffman-encode "abcdef")))', env)
        assert decoded == original

    def test_roundtrip_sentence(self, huffman_env_and_output):
        """Test round-trip on a realistic sentence with spaces."""
        env, _ = huffman_env_and_output
        original = "the quick brown fox"
        decoded = eval_source('(huffman-decode (car (huffman-encode "the quick brown fox")) (cadr (huffman-encode "the quick brown fox")))', env)
        assert decoded == original

    def test_roundtrip_empty(self, huffman_env_and_output):
        """Test round-trip on empty string."""
        env, _ = huffman_env_and_output
        original = ""
        decoded = eval_source('(huffman-decode (car (huffman-encode "")) (cadr (huffman-encode "")))', env)
        assert decoded == original

    def test_roundtrip_single_char(self, huffman_env_and_output):
        """Test round-trip on single character."""
        env, _ = huffman_env_and_output
        original = "x"
        decoded = eval_source('(huffman-decode (car (huffman-encode "x")) (cadr (huffman-encode "x")))', env)
        assert decoded == original


class TestSingleCharacter:
    """Test special case: single distinct character."""

    def test_single_char_codes(self, huffman_env_and_output):
        """Test that single character maps to code '0'."""
        env, _ = huffman_env_and_output
        # Build tree from frequency of single character
        result = eval_source('(huffman-encode "aaaa")', env)
        tree = eval_source('(car (huffman-encode "aaaa"))', env)
        codes = eval_source('(huffman-codes (car (huffman-encode "aaaa")))', env)
        # Extract the code for "a"
        code = eval_source('(hash-ref (huffman-codes (car (huffman-encode "aaaa"))) "a")', env)
        assert code == "0"

    def test_single_char_roundtrip(self, huffman_env_and_output):
        """Test round-trip for single-character string."""
        env, _ = huffman_env_and_output
        original = "zzzz"
        decoded = eval_source('(huffman-decode (car (huffman-encode "zzzz")) (cadr (huffman-encode "zzzz")))', env)
        assert decoded == original


class TestPrefixFree:
    """Test prefix-free property of generated codes."""

    def test_prefix_free_two_chars(self, huffman_env_and_output):
        """Test prefix-free property for two-character string."""
        env, _ = huffman_env_and_output
        # Generate codes for "aabb"
        codes = eval_source('(huffman-codes (car (huffman-encode "aabb")))', env)
        code_a = eval_source('(hash-ref (huffman-codes (car (huffman-encode "aabb"))) "a")', env)
        code_b = eval_source('(hash-ref (huffman-codes (car (huffman-encode "aabb"))) "b")', env)
        # No code should be a prefix of the other
        # If both have length > 0, check they're not prefixes
        assert not (code_a == code_b)
        # For equal frequencies, neither should be a prefix of the other
        if len(code_a) < len(code_b):
            assert not code_b.startswith(code_a)
        elif len(code_b) < len(code_a):
            assert not code_a.startswith(code_b)

    def test_prefix_free_skewed(self, huffman_env_and_output):
        """Test prefix-free property for skewed frequency distribution."""
        env, _ = huffman_env_and_output
        # Very skewed: lots of 'a', few others
        original = "aaaaaaaaaaabcd"
        codes = eval_source('(huffman-codes (car (huffman-encode "aaaaaaaaaaabcd")))', env)
        code_a = eval_source('(hash-ref (huffman-codes (car (huffman-encode "aaaaaaaaaaabcd"))) "a")', env)
        code_b = eval_source('(hash-ref (huffman-codes (car (huffman-encode "aaaaaaaaaaabcd"))) "b")', env)
        code_c = eval_source('(hash-ref (huffman-codes (car (huffman-encode "aaaaaaaaaaabcd"))) "c")', env)
        code_d = eval_source('(hash-ref (huffman-codes (car (huffman-encode "aaaaaaaaaaabcd"))) "d")', env)
        codes_list = [code_a, code_b, code_c, code_d]
        # Check all pairs: no code is prefix of another
        for i in range(len(codes_list)):
            for j in range(len(codes_list)):
                if i != j:
                    ci = codes_list[i]
                    cj = codes_list[j]
                    if len(ci) < len(cj):
                        assert not cj.startswith(ci), f"Code {ci} is prefix of {cj}"
                    elif len(cj) < len(ci):
                        assert not ci.startswith(cj), f"Code {cj} is prefix of {ci}"


class TestBitStringProperties:
    """Test properties of the encoded bit string."""

    def test_bits_only_zero_one(self, huffman_env_and_output):
        """Test that encoded bits contain only '0' and '1'."""
        env, _ = huffman_env_and_output
        bits = eval_source('(cadr (huffman-encode "the quick brown fox"))', env)
        # All characters should be '0' or '1'
        for ch in bits:
            assert ch in ['0', '1']

    def test_bits_empty_string(self, huffman_env_and_output):
        """Test that empty string produces empty bit string."""
        env, _ = huffman_env_and_output
        bits = eval_source('(cadr (huffman-encode ""))', env)
        assert bits == ""

    def test_bits_non_empty(self, huffman_env_and_output):
        """Test that non-empty string produces non-empty bit string."""
        env, _ = huffman_env_and_output
        bits = eval_source('(cadr (huffman-encode "a"))', env)
        assert len(bits) > 0
        assert bits == "0"  # Single char gets code "0"


class TestCompressionSanity:
    """Test that compression is better than fixed-width encoding."""

    def test_compression_skewed(self, huffman_env_and_output):
        """Test compression on skewed distribution."""
        env, _ = huffman_env_and_output
        # Create a string with very skewed character distribution
        # 1000 'a's, 1 each of 'b', 'c', 'd' = 1003 chars total
        # Fixed-width encoding: 1003 chars * 2 bits (to distinguish 4 symbols) = 2006 bits
        # Huffman should be much better
        original = "a" * 100 + "bcd"
        bits = eval_source('(cadr (huffman-encode "' + original + '"))', env)
        fixed_width_bits = len(original) * 2  # 2 bits per char for 4 distinct symbols
        # Huffman should be strictly less
        assert len(bits) < fixed_width_bits, \
            f"Huffman {len(bits)} should be < fixed-width {fixed_width_bits}"

    def test_compression_moderate(self, huffman_env_and_output):
        """Test that moderate skew still improves over fixed-width."""
        env, _ = huffman_env_and_output
        # String with moderate skew
        original = "aaabbc"  # 6 chars, 3 distinct (needs 2 bits each in fixed-width)
        bits = eval_source('(cadr (huffman-encode "aaabbc"))', env)
        fixed_width_bits = 6 * 2  # 12 bits
        # Huffman encodes 'a' in 1 bit, 'b' and 'c' in 2 bits: 3*1 + 1*2 + 1*2 = 7 bits
        assert len(bits) <= fixed_width_bits
        assert len(bits) < fixed_width_bits, \
            f"Huffman {len(bits)} should be < fixed-width {fixed_width_bits}"
