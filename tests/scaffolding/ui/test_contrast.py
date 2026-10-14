"""Token pairs used together clear WCAG AA, resolved the way the browser would.

The resolver implements exactly the expressions `tokens.css` uses - `var()`
and srgb `color-mix()` - so the test reads the same file Chrome does. It does
not parse CSS in general; a new expression form in tokens.css should extend
`rgb` or fail loudly here.
"""

import re
from pathlib import Path

import pytest

from scaffolding import ui

TOKENS = Path(ui.__file__).parent / "static" / "ui" / "tokens.css"

# Every pair one of our stylesheets actually lays on the other. Grows with use.
PAIRS = [
    ("ink", "bg"),
    ("ink-quiet", "bg"),
    ("brand", "bg"),
    ("brand-ink", "brand"),
    ("brand-ink", "danger"),
    ("brand-ink", "ok"),
    ("danger", "bg"),
]


def declarations() -> dict[str, str]:
    """`--name: value;` lines of tokens.css, one declaration per line by style."""
    found = re.findall(r"^\s*--([a-z0-9-]+):\s*(.+);", TOKENS.read_text(), flags=re.MULTILINE)
    return dict(found)


def rgb(value: str, table: dict[str, str]) -> tuple[float, float, float]:
    """A color expression to srgb channels in 0..255."""
    value = value.strip()
    if value.startswith("var(--"):
        return rgb(table[value[6:].rstrip(")")], table)
    mixed = re.fullmatch(r"color-mix\(in srgb,\s*(.+?),\s*(.+?)\s+(\d+)%\)", value)
    if mixed:
        base, other, percent = rgb(mixed.group(1), table), rgb(mixed.group(2), table), int(mixed.group(3))
        blend = tuple(b * (1 - percent / 100) + o * percent / 100 for b, o in zip(base, other, strict=True))
        return (blend[0], blend[1], blend[2])
    hexed = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value)
    if hexed:
        digits = hexed.group(1)
        if len(digits) == 3:
            digits = "".join(character * 2 for character in digits)
        return (int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16))
    raise ValueError(f"tokens.css grew an expression this resolver does not speak: {value}")


def luminance(channels: tuple[float, float, float]) -> float:
    def linear(channel: float) -> float:
        scaled = channel / 255
        return scaled / 12.92 if scaled <= 0.03928 else ((scaled + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(fore: str, back: str) -> float:
    table = declarations()
    lighter, darker = sorted(
        (luminance(rgb(f"var(--{fore})", table)), luminance(rgb(f"var(--{back})", table))), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


@pytest.mark.parametrize("fore,back", PAIRS)
def test_the_pair_clears_aa(fore: str, back: str) -> None:
    assert contrast(fore, back) >= 4.5, f"--{fore} on --{back} is {contrast(fore, back):.2f}, below 4.5"


def test_there_are_pairs_to_check() -> None:
    assert len(PAIRS) >= 5
