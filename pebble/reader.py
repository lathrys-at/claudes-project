"""Tokenizer and parser for Pebble source code."""
from pebble.types import Symbol, PebbleList, NIL


class ReadError(Exception):
    """Raised when there is an error reading Pebble source code."""
    pass


def tokenize(source: str) -> list[str]:
    """Tokenize Pebble source code into a list of tokens.

    Whitespace separates tokens. Parentheses, single-quote, backtick, comma, and ,@ are their own tokens.
    Strings are delimited by double quotes and may contain escape sequences.
    Comments (;) run to end of line and are ignored.
    """
    tokens = []
    i = 0
    while i < len(source):
        # Skip whitespace
        if source[i].isspace():
            i += 1
            continue

        # Comments: ; to end of line
        if source[i] == ';':
            while i < len(source) and source[i] != '\n':
                i += 1
            continue

        # Parentheses and quote are single-character tokens
        if source[i] in '()\'' + '`':
            tokens.append(source[i])
            i += 1
            continue

        # Comma: check for ,@ (two-character token) or , (single)
        if source[i] == ',':
            if i + 1 < len(source) and source[i + 1] == '@':
                tokens.append(',@')
                i += 2
            else:
                tokens.append(',')
                i += 1
            continue

        # Strings: delimited by double quotes, support escapes
        if source[i] == '"':
            j = i + 1
            while j < len(source):
                if source[j] == '\\' and j + 1 < len(source):
                    j += 2  # Skip escape sequence
                elif source[j] == '"':
                    tokens.append(source[i:j+1])
                    i = j + 1
                    break
                else:
                    j += 1
            else:
                # Unterminated string
                raise ReadError(f"Unterminated string at position {i}")
            continue

        # Regular token: non-whitespace, non-special characters
        j = i
        while j < len(source) and not source[j].isspace() and source[j] not in '()\'"`;,':
            j += 1
        if j > i:
            tokens.append(source[i:j])
            i = j

    return tokens


def _parse_tokens(tokens: list[str], index: int = 0) -> tuple:
    """Parse tokens into Pebble values. Returns (value, next_index)."""
    if index >= len(tokens):
        raise ReadError("Unexpected end of input")

    token = tokens[index]

    # Opening paren: read a list
    if token == '(':
        items = []
        index += 1
        while index < len(tokens) and tokens[index] != ')':
            value, index = _parse_tokens(tokens, index)
            items.append(value)
        if index >= len(tokens):
            raise ReadError("Unbalanced parentheses: missing ')'")
        return PebbleList(items), index + 1

    # Closing paren: error
    if token == ')':
        raise ReadError("Unexpected ')'")

    # Quote: 'x becomes (quote x)
    if token == "'":
        value, index = _parse_tokens(tokens, index + 1)
        return PebbleList([Symbol("quote"), value]), index

    # Quasiquote: `x becomes (quasiquote x)
    if token == "`":
        value, index = _parse_tokens(tokens, index + 1)
        return PebbleList([Symbol("quasiquote"), value]), index

    # Unquote: ,x becomes (unquote x)
    if token == ",":
        value, index = _parse_tokens(tokens, index + 1)
        return PebbleList([Symbol("unquote"), value]), index

    # Unquote-splicing: ,@x becomes (unquote-splicing x)
    if token == ",@":
        value, index = _parse_tokens(tokens, index + 1)
        return PebbleList([Symbol("unquote-splicing"), value]), index

    # String: remove quotes and process escapes
    if token.startswith('"') and token.endswith('"'):
        s = token[1:-1]
        # Process escape sequences
        s = s.replace('\\n', '\n')
        s = s.replace('\\\\', '\x00')  # Temporary placeholder
        s = s.replace('\\"', '"')
        s = s.replace('\x00', '\\')    # Replace placeholder back
        return s, index + 1

    # Boolean literals
    if token == 'true':
        return True, index + 1
    if token == 'false':
        return False, index + 1

    # Nil
    if token == 'nil':
        return NIL, index + 1

    # Try to parse as number
    try:
        # Try integer first
        if '.' not in token:
            return int(token), index + 1
        else:
            return float(token), index + 1
    except ValueError:
        pass

    # Default: symbol
    return Symbol(token), index + 1


def read(source: str) -> list:
    """Read all top-level forms from source and return as a list of Pebble values."""
    tokens = tokenize(source)
    forms = []
    index = 0
    while index < len(tokens):
        value, index = _parse_tokens(tokens, index)
        forms.append(value)
    return forms


def read_one(source: str):
    """Read exactly one form from source. Raise ReadError if there is leftover input or no form."""
    tokens = tokenize(source)
    if not tokens:
        raise ReadError("No form to read")
    value, index = _parse_tokens(tokens, 0)
    if index < len(tokens):
        raise ReadError(f"Unexpected input after form: {tokens[index]}")
    return value
