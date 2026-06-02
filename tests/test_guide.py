"""Test that all code examples in docs/GUIDE.md are correct and up-to-date.

This test:
1. Reads the GUIDE.md file
2. Extracts all ```pebble code blocks
3. For each block:
   - Evaluates all forms in a fresh environment
   - Verifies that no form raises an error
   - Checks that all `; => RESULT` annotations match the actual evaluated result
4. Asserts that a reasonable number of annotations were checked (>= 20)

This ensures the guide documentation never drifts from the actual interpreter behavior.
"""

import re
from pathlib import Path
from pebble.evaluator import make_global_env, EvalError
from pebble.reader import read, ReadError
from pebble.printer import pebble_repr


def extract_pebble_blocks(guide_path):
    """Extract all ```pebble code blocks from the GUIDE.md file.

    Returns a list of (block_number, lines) where lines is a list of strings.
    """
    with open(guide_path, "r") as f:
        content = f.read()

    # Find all ```pebble ... ``` blocks
    pattern = r"```pebble\n(.*?)\n```"
    matches = list(re.finditer(pattern, content, re.DOTALL))

    blocks = []
    for i, match in enumerate(matches):
        block_text = match.group(1)
        lines = block_text.split("\n")
        blocks.append((i, lines))

    return blocks


def parse_block_with_annotations(block_text):
    """Parse a pebble code block to extract source code and line-based annotations.

    Returns a tuple (source_code, annotations) where:
    - source_code is the full block source (stripped of comments/empty lines)
    - annotations is a dict mapping original lines (in block_text) to their expected result

    We preserve the structure of multi-line forms and find annotations on the last line.
    """
    lines = block_text.strip().split('\n')

    # Collect non-empty, non-pure-comment lines
    code_lines = []
    annotations = {}  # Map from concatenated_form_text -> expected_result

    current_form_lines = []
    current_form_start = 0

    for i, line in enumerate(lines):
        line = line.rstrip()

        # Skip empty lines and pure comment lines
        if not line.strip() or line.strip().startswith(";"):
            if current_form_lines:
                # Save the accumulated form
                form_text = '\n'.join(current_form_lines)
                code_lines.append(form_text)
                current_form_lines = []
            continue

        # Check if this line has an annotation
        match = re.search(r"^(.*?)\s*;\s*=>\s*(.+)$", line)
        if match:
            code_part = match.group(1).strip()
            result = match.group(2).strip()
            current_form_lines.append(code_part)
            form_text = '\n'.join(current_form_lines)
            code_lines.append(form_text)
            annotations[form_text] = result
            current_form_lines = []
        else:
            current_form_lines.append(line)

    # Don't forget the last form if it wasn't terminated
    if current_form_lines:
        form_text = '\n'.join(current_form_lines)
        code_lines.append(form_text)

    source_code = '\n'.join(code_lines)
    return source_code, annotations


def test_guide_blocks():
    """Test all code blocks in the guide."""
    guide_path = Path(__file__).parent.parent / "docs" / "GUIDE.md"
    assert guide_path.exists(), f"Guide not found at {guide_path}"

    blocks = extract_pebble_blocks(guide_path)
    assert len(blocks) > 0, "No ```pebble blocks found in guide"

    total_annotations_checked = 0

    # Test each block
    for block_num, lines in blocks:
        # Create a fresh environment for each block
        env = make_global_env()

        # Parse the block to get source and annotations
        block_text = '\n'.join(lines)
        source_code, annotations = parse_block_with_annotations(block_text)

        if not source_code.strip():
            continue  # Skip empty blocks

        # Try to parse the whole block
        try:
            forms = read(source_code)
        except ReadError as e:
            raise AssertionError(
                f"Block {block_num}: Failed to parse:\n{source_code}\n"
                f"Error: {e}"
            ) from e

        # Evaluate all forms
        try:
            for form in forms:
                _eval_expr(form, env)
        except EvalError as e:
            raise AssertionError(
                f"Block {block_num}: Evaluation error:\n{source_code}\n"
                f"Error: {e}"
            ) from e

        # For annotation checking, re-evaluate each annotated form
        for form_code, expected_result in annotations.items():
            try:
                expr_forms = read(form_code)
                expr_result = None
                for expr in expr_forms:
                    expr_result = _eval_expr(expr, env)

                actual_repr = pebble_repr(expr_result)

                if actual_repr != expected_result:
                    raise AssertionError(
                        f"Block {block_num}, annotation mismatch:\n"
                        f"Code: {form_code}\n"
                        f"Expected: {expected_result}\n"
                        f"Got: {actual_repr}"
                    )

                total_annotations_checked += 1
            except ReadError as e:
                raise AssertionError(
                    f"Block {block_num}: Failed to parse annotated form:\n"
                    f"{form_code}\nError: {e}"
                ) from e

    # Sanity check: ensure we tested a reasonable number of annotations
    assert total_annotations_checked >= 20, (
        f"Expected to check at least 20 annotations, but only checked "
        f"{total_annotations_checked}. The guide may be missing examples."
    )


def _eval_expr(expr, env):
    """Evaluate an expression in the given environment.

    Uses seval which handles tail-call trampolining internally.
    """
    from pebble.evaluator import seval

    return seval(expr, env)


if __name__ == "__main__":
    test_guide_blocks()
    print("All guide examples verified!")
