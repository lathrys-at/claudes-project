"""Tests for quasiquote, unquote, and unquote-splicing."""
import pytest
from pebble.reader import read, read_one, ReadError
from pebble.types import Symbol, PebbleList, NIL
from pebble.evaluator import seval, make_global_env, eval_source, EvalError


class TestQuasiquoteReader:
    """Test reader support for quasiquote syntax."""

    def test_backtick_reads_as_quasiquote(self):
        """Backtick `x should read as (quasiquote x)."""
        result = read_one("`x")
        expected = PebbleList([Symbol("quasiquote"), Symbol("x")])
        assert result == expected

    def test_comma_reads_as_unquote(self):
        """,x should read as (unquote x)."""
        result = read_one(",x")
        expected = PebbleList([Symbol("unquote"), Symbol("x")])
        assert result == expected

    def test_comma_at_reads_as_unquote_splicing(self):
        """,@x should read as (unquote-splicing x)."""
        result = read_one(",@x")
        expected = PebbleList([Symbol("unquote-splicing"), Symbol("x")])
        assert result == expected

    def test_combined_template(self):
        """`(a ,b ,@c d) should read to correct nested structure."""
        result = read_one("`(a ,b ,@c d)")
        expected = PebbleList([
            Symbol("quasiquote"),
            PebbleList([
                Symbol("a"),
                PebbleList([Symbol("unquote"), Symbol("b")]),
                PebbleList([Symbol("unquote-splicing"), Symbol("c")]),
                Symbol("d")
            ])
        ])
        assert result == expected

    def test_backtick_and_comma_terminate_symbols(self):
        """Backtick and comma should terminate symbol parsing."""
        # Test tokenizer behavior: a`b should read as two separate forms
        forms = read("a`b")
        assert len(forms) == 2
        assert forms[0] == Symbol("a")
        assert forms[1] == PebbleList([Symbol("quasiquote"), Symbol("b")])

    def test_comma_terminates_symbol(self):
        """Comma should terminate symbol parsing."""
        forms = read("a,b")
        assert len(forms) == 2
        assert forms[0] == Symbol("a")
        assert forms[1] == PebbleList([Symbol("unquote"), Symbol("b")])


class TestQuasiquoteEvaluator:
    """Test evaluator support for quasiquote."""

    def test_quasiquote_literal_number(self):
        """`5 should evaluate to 5."""
        env = make_global_env()
        result = seval(read_one("`5"), env)
        assert result == 5

    def test_quasiquote_literal_symbol(self):
        """`x should evaluate to Symbol x without evaluation."""
        env = make_global_env()
        result = seval(read_one("`x"), env)
        assert result == Symbol("x")

    def test_quasiquote_literal_list(self):
        """`(1 2 3) should evaluate to PebbleList(1, 2, 3)."""
        env = make_global_env()
        result = seval(read_one("`(1 2 3)"), env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_quasiquote_with_unquote(self):
        """With (define x 10), `(a ,x b) should evaluate to (a 10 b)."""
        env = make_global_env()
        seval(read_one("(define x 10)"), env)
        result = seval(read_one("`(a ,x b)"), env)
        expected = PebbleList([Symbol("a"), 10, Symbol("b")])
        assert result == expected

    def test_unquote_splice_basic(self):
        """With (define xs (list 1 2 3)), `(0 ,@xs 4) should splice the list."""
        env = make_global_env()
        seval(read_one("(define xs (list 1 2 3))"), env)
        result = seval(read_one("`(0 ,@xs 4)"), env)
        expected = PebbleList([0, 1, 2, 3, 4])
        assert result == expected

    def test_unquote_splice_middle(self):
        """Splicing in the middle of a list."""
        env = make_global_env()
        seval(read_one("(define xs (list 2 3))"), env)
        result = seval(read_one("`(1 ,@xs 4)"), env)
        expected = PebbleList([1, 2, 3, 4])
        assert result == expected

    def test_unquote_splice_end(self):
        """Splicing at the end of a list."""
        env = make_global_env()
        seval(read_one("(define xs (list 2 3 4))"), env)
        result = seval(read_one("`(1 ,@xs)"), env)
        expected = PebbleList([1, 2, 3, 4])
        assert result == expected

    def test_computed_unquote(self):
        """With x=10, `(sum is ,(+ x 5)) should evaluate the expression."""
        env = make_global_env()
        seval(read_one("(define x 10)"), env)
        result = seval(read_one("`(sum is ,(+ x 5))"), env)
        expected = PebbleList([Symbol("sum"), Symbol("is"), 15])
        assert result == expected

    def test_unquote_splice_non_list_raises_error(self):
        """unquote-splicing of a non-list should raise EvalError."""
        env = make_global_env()
        seval(read_one("(define x 5)"), env)
        with pytest.raises(EvalError, match="unquote-splicing: expected a list"):
            seval(read_one("`(1 ,@x 2)"), env)

    def test_nested_quasiquote(self):
        """Nested quasiquote should preserve inner unquote/quasiquote at depth 2.

        `(a `(b ,(c))) should NOT evaluate ,(c) since it's at depth 2.
        The inner ,(c) should be preserved as (unquote (c)).
        """
        env = make_global_env()
        result = seval(read_one("`(a `(b ,(c)))"), env)

        # The outer quasiquote expands at depth 1
        # The inner `` `(b ,(c)) `` becomes (quasiquote (b (unquote (c))))
        # So result should be:
        # (a (quasiquote (b (unquote (c)))))
        expected = PebbleList([
            Symbol("a"),
            PebbleList([
                Symbol("quasiquote"),
                PebbleList([
                    Symbol("b"),
                    PebbleList([Symbol("unquote"), PebbleList([Symbol("c")])])
                ])
            ])
        ])
        assert result == expected

    def test_empty_quasiquote(self):
        """`() should evaluate to empty PebbleList."""
        env = make_global_env()
        result = seval(read_one("`()"), env)
        expected = NIL
        assert result == expected

    def test_quasiquote_with_multiple_unquotes(self):
        """Multiple unquotes in one quasiquote."""
        env = make_global_env()
        seval(read_one("(define a 1)"), env)
        seval(read_one("(define b 2)"), env)
        seval(read_one("(define c 3)"), env)
        result = seval(read_one("`(,a ,b ,c)"), env)
        expected = PebbleList([1, 2, 3])
        assert result == expected

    def test_quasiquote_requires_exactly_one_argument(self):
        """quasiquote must have exactly 1 argument."""
        env = make_global_env()
        # No arguments
        with pytest.raises(EvalError, match="quasiquote requires exactly 1 argument"):
            seval(read_one("(quasiquote)"), env)
        # Too many arguments
        with pytest.raises(EvalError, match="quasiquote requires exactly 1 argument"):
            seval(read_one("(quasiquote a b)"), env)

    def test_multiple_unquote_splices(self):
        """Multiple unquote-splices in one quasiquote."""
        env = make_global_env()
        seval(read_one("(define xs (list 1 2))"), env)
        seval(read_one("(define ys (list 3 4))"), env)
        result = seval(read_one("`(,@xs ,@ys)"), env)
        expected = PebbleList([1, 2, 3, 4])
        assert result == expected

    def test_unquote_splice_empty_list(self):
        """Splicing an empty list should have no effect."""
        env = make_global_env()
        seval(read_one("(define xs (list))"), env)
        result = seval(read_one("`(1 ,@xs 2)"), env)
        expected = PebbleList([1, 2])
        assert result == expected

    def test_nested_lists_in_quasiquote(self):
        """Quasiquote with nested lists."""
        env = make_global_env()
        seval(read_one("(define x 10)"), env)
        result = seval(read_one("`((a ,x) (b 20))"), env)
        expected = PebbleList([
            PebbleList([Symbol("a"), 10]),
            PebbleList([Symbol("b"), 20])
        ])
        assert result == expected

    def test_string_in_quasiquote(self):
        """Strings should be self-quoting in quasiquote."""
        env = make_global_env()
        result = seval(read_one('`("hello" "world")'), env)
        expected = PebbleList(["hello", "world"])
        assert result == expected

    def test_boolean_in_quasiquote(self):
        """Booleans should be self-quoting in quasiquote."""
        env = make_global_env()
        result = seval(read_one("`(true false)"), env)
        expected = PebbleList([True, False])
        assert result == expected

    def test_deeply_nested_quasiquote(self):
        """Three levels of quasiquote nesting."""
        env = make_global_env()
        # ``(,(+ 1 2)) at depth 2, the ,(+ 1 2) should be preserved at depth 2
        result = seval(read_one("``(,(+ 1 2))"), env)
        expected = PebbleList([
            Symbol("quasiquote"),
            PebbleList([
                PebbleList([Symbol("unquote"), PebbleList([Symbol("+"), 1, 2])])
            ])
        ])
        assert result == expected

    def test_quote_and_quasiquote_different(self):
        """quote and quasiquote should be different."""
        env = make_global_env()
        seval(read_one("(define x 10)"), env)

        # quote does not evaluate
        quoted = seval(read_one("'(a ,x b)"), env)
        expected_quote = PebbleList([
            Symbol("a"),
            PebbleList([Symbol("unquote"), Symbol("x")]),
            Symbol("b")
        ])
        assert quoted == expected_quote

        # quasiquote evaluates the unquote
        quasiquoted = seval(read_one("`(a ,x b)"), env)
        expected_quasi = PebbleList([Symbol("a"), 10, Symbol("b")])
        assert quasiquoted == expected_quasi
