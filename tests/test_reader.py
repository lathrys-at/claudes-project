"""Tests for the Pebble reader (tokenizer and parser)."""
import pytest
from pebble.reader import tokenize, read, read_one, ReadError
from pebble.types import Symbol, PebbleList, NIL


class TestTokenize:
    """Tests for the tokenize function."""

    def test_simple_form(self):
        """Tokenizing a simple form like (+ 1 2)."""
        tokens = tokenize("(+ 1 2)")
        assert tokens == ["(", "+", "1", "2", ")"]

    def test_string_with_spaces(self):
        """Tokenizing a string with spaces."""
        tokens = tokenize('(print "hello world")')
        assert tokens == ["(", "print", '"hello world"', ")"]

    def test_string_with_escapes(self):
        """Tokenizing a string with escape sequences."""
        tokens = tokenize(r'"hello \"world\" \\ \n"')
        assert tokens == [r'"hello \"world\" \\ \n"']

    def test_comments_ignored(self):
        """Comments are ignored."""
        tokens = tokenize("(+ 1 2) ; this is a comment")
        assert tokens == ["(", "+", "1", "2", ")"]

    def test_comments_to_end_of_line(self):
        """Comments run to end of line."""
        tokens = tokenize("(+ 1 ; comment\n 2)")
        assert tokens == ["(", "+", "1", "2", ")"]

    def test_multiline_input(self):
        """Multiple lines with comments."""
        source = """
        (define x 10)
        ; comment here
        (+ x 5)
        """
        tokens = tokenize(source)
        assert tokens == ["(", "define", "x", "10", ")", "(", "+", "x", "5", ")"]

    def test_nested_lists(self):
        """Tokenizing nested lists."""
        tokens = tokenize("(a (b c) d)")
        assert tokens == ["(", "a", "(", "b", "c", ")", "d", ")"]

    def test_quote_token(self):
        """Single quote is its own token."""
        tokens = tokenize("'x")
        assert tokens == ["'", "x"]


class TestParseAtoms:
    """Tests for parsing individual atoms."""

    def test_integers(self):
        """Reading integers."""
        assert read_one("42") == 42
        assert read_one("-5") == -5
        assert read_one("+10") == 10
        assert read_one("0") == 0

    def test_floats(self):
        """Reading floats."""
        assert read_one("3.14") == 3.14
        assert read_one("-2.5") == -2.5
        assert read_one("0.0") == 0.0

    def test_true_false(self):
        """Reading booleans."""
        assert read_one("true") is True
        assert read_one("false") is False

    def test_nil(self):
        """Reading nil."""
        result = read_one("nil")
        assert result == NIL
        assert isinstance(result, PebbleList)
        assert len(result) == 0

    def test_symbols(self):
        """Reading symbols."""
        result = read_one("foo")
        assert isinstance(result, Symbol)
        assert result == "foo"

    def test_string_basic(self):
        """Reading strings."""
        assert read_one('"hello"') == "hello"
        assert read_one('"hello world"') == "hello world"

    def test_string_with_escapes(self):
        """Strings with escape sequences decode correctly."""
        assert read_one(r'"hello\"world"') == 'hello"world'
        assert read_one(r'"line1\nline2"') == "line1\nline2"
        assert read_one(r'"backslash\\"') == "backslash\\"


class TestParseLists:
    """Tests for parsing lists."""

    def test_empty_list(self):
        """Empty lists."""
        result = read_one("()")
        assert result == NIL
        assert isinstance(result, PebbleList)

    def test_simple_list(self):
        """Simple list like (+ 1 2)."""
        result = read_one("(+ 1 2)")
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == Symbol("+")
        assert result[1] == 1
        assert result[2] == 2

    def test_nested_lists(self):
        """Nested lists like (a (b c) d)."""
        result = read_one("(a (b c) d)")
        assert isinstance(result, PebbleList)
        assert len(result) == 3
        assert result[0] == Symbol("a")
        assert isinstance(result[1], PebbleList)
        assert len(result[1]) == 2
        assert result[1][0] == Symbol("b")
        assert result[1][1] == Symbol("c")
        assert result[2] == Symbol("d")

    def test_deeply_nested(self):
        """Deeply nested lists."""
        result = read_one("(((())))")
        assert isinstance(result, PebbleList)
        assert len(result) == 1
        inner = result[0]
        assert isinstance(inner, PebbleList)
        assert len(inner) == 1
        inner = inner[0]
        assert isinstance(inner, PebbleList)
        assert len(inner) == 1
        inner = inner[0]
        assert isinstance(inner, PebbleList)
        assert len(inner) == 0


class TestQuote:
    """Tests for the quote special form."""

    def test_quote_symbol(self):
        """Quote: 'x reads as (quote x)."""
        result = read_one("'x")
        assert isinstance(result, PebbleList)
        assert len(result) == 2
        assert result[0] == Symbol("quote")
        assert result[1] == Symbol("x")

    def test_quote_number(self):
        """Quote a number."""
        result = read_one("'42")
        assert isinstance(result, PebbleList)
        assert len(result) == 2
        assert result[0] == Symbol("quote")
        assert result[1] == 42

    def test_quote_list(self):
        """Quote a list."""
        result = read_one("'(a b c)")
        assert isinstance(result, PebbleList)
        assert len(result) == 2
        assert result[0] == Symbol("quote")
        quoted_list = result[1]
        assert isinstance(quoted_list, PebbleList)
        assert len(quoted_list) == 3
        assert quoted_list[0] == Symbol("a")

    def test_nested_quotes(self):
        """Nested quotes."""
        result = read_one("''x")
        assert isinstance(result, PebbleList)
        assert result[0] == Symbol("quote")
        inner = result[1]
        assert isinstance(inner, PebbleList)
        assert inner[0] == Symbol("quote")
        assert inner[1] == Symbol("x")


class TestReadMultipleForms:
    """Tests for reading multiple top-level forms."""

    def test_read_multiple(self):
        """read() returns all top-level forms."""
        result = read("(+ 1 2) (+ 3 4)")
        assert len(result) == 2
        assert isinstance(result[0], PebbleList)
        assert isinstance(result[1], PebbleList)
        assert result[0][0] == Symbol("+")
        assert result[1][0] == Symbol("+")

    def test_read_atoms(self):
        """read() with atoms."""
        result = read("1 2 3")
        assert result == [1, 2, 3]

    def test_read_mixed(self):
        """read() with mixed forms."""
        result = read("42 (+ 1 2) foo")
        assert len(result) == 3
        assert result[0] == 42
        assert isinstance(result[1], PebbleList)
        assert result[2] == Symbol("foo")

    def test_read_empty(self):
        """read() on empty or whitespace-only input."""
        assert read("") == []
        assert read("   ") == []
        assert read("; comment\n") == []


class TestErrors:
    """Tests for error conditions."""

    def test_unbalanced_parens_missing_close(self):
        """Unbalanced parentheses: missing )."""
        with pytest.raises(ReadError):
            read_one("(+ 1 2")

    def test_unbalanced_parens_extra_close(self):
        """Unbalanced parentheses: extra )."""
        with pytest.raises(ReadError):
            read_one("(+ 1 2))")

    def test_extra_close_alone(self):
        """Extra closing paren by itself."""
        with pytest.raises(ReadError):
            read_one(")")

    def test_read_one_empty(self):
        """read_one on empty input."""
        with pytest.raises(ReadError):
            read_one("")

    def test_read_one_whitespace_only(self):
        """read_one on whitespace-only input."""
        with pytest.raises(ReadError):
            read_one("   ")

    def test_read_one_with_trailing_input(self):
        """read_one raises ReadError on trailing input."""
        with pytest.raises(ReadError):
            read_one("42 trailing")

    def test_read_one_with_trailing_form(self):
        """read_one raises ReadError when multiple forms present."""
        with pytest.raises(ReadError):
            read_one("(a) (b)")

    def test_unterminated_string(self):
        """Unterminated string raises ReadError."""
        with pytest.raises(ReadError):
            read_one('"unterminated')


class TestComplexExamples:
    """Tests for more complex, realistic Pebble code."""

    def test_function_definition(self):
        """Parsing a function definition-like form."""
        result = read_one("(defn square (x) (* x x))")
        assert isinstance(result, PebbleList)
        assert len(result) == 4
        assert result[0] == Symbol("defn")
        assert result[1] == Symbol("square")
        assert isinstance(result[2], PebbleList)
        assert result[2][0] == Symbol("x")

    def test_quoted_list_in_list(self):
        """Lists containing quoted forms."""
        result = read_one("(list 'a 'b 'c)")
        assert isinstance(result, PebbleList)
        assert result[0] == Symbol("list")
        assert isinstance(result[1], PebbleList)
        assert result[1][0] == Symbol("quote")

    def test_mixed_types(self):
        """Lists with mixed data types."""
        result = read_one('(msg "hello" 42 true nil my-symbol)')
        assert isinstance(result, PebbleList)
        assert result[0] == Symbol("msg")
        assert result[1] == "hello"
        assert result[2] == 42
        assert result[3] is True
        assert result[4] == NIL
        assert result[5] == Symbol("my-symbol")
