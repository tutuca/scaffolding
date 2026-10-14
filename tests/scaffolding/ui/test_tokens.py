"""Colors live in tokens.css, so the contrast test can see every one.

`test_contrast.py` resolves each token pair through the same file Chrome reads;
this holds the precondition - no literal color anywhere else can slip past it.
"""

import re
from pathlib import Path

import pytest

from scaffolding import ui

UI = Path(ui.__file__).parent
TOKENS = UI / "static" / "ui" / "tokens.css"

# `(?<!&)` so an HTML entity like `&#10006;` - all decimal digits are hex
# digits - does not read as a color. Found by vendoring change_list.html.
COLOR_LITERAL = re.compile(r"(?<!&)#[0-9a-fA-F]{3,8}\b|\brgba?\(")

# Every file of ours that could name a color.
DRESSED = sorted(UI.rglob("*.css")) + sorted(UI.rglob("*.html"))


@pytest.mark.parametrize("path", [path for path in DRESSED if path != TOKENS], ids=lambda path: path.name)
def test_no_color_literal_outside_tokens(path: Path) -> None:
    """A stray literal color is invisible to `test_contrast.py`; the review that
    reads it has no contrast number. Colors belong in tokens.css."""
    strays = [line for line in path.read_text().splitlines() if COLOR_LITERAL.search(line)]
    assert not strays, f"{path.name} names a color; it belongs in tokens.css: {strays}"
