#!/usr/bin/env python
"""What changed between two sets of shots, in pixels.

`bin/ui_shot.py --out var/shots-baseline` keeps a baseline; this compares a fresh
`var/shots` (or any directory) with it, shot by shot. Two shots of one page differ
by more than code: the ledger moves, a clock ticks, a chart's tick lands one pixel
over. So the report is a share of changed pixels per shot and a picture of where -
`var/shots-diff/<name>.png`, the new shot with changed pixels in red - and judging
whether a change is the data or the code is the reader's, with the pictures.

A shot whose height moved is compared over the height they share and says so: a
longer page is a change, whatever the top of it looks like.
"""

import argparse
from pathlib import Path

from PIL import Image, ImageChops

# A channel must move this much (of 255) to count: smooths the antialiasing of a glyph
# that landed on a different subpixel without hiding a colour that changed.
CHANNEL = 12


def compare(before: Path, after: Path, picture: Path) -> tuple[float, tuple[int, int], tuple[int, int]]:
    """The share of pixels that changed over the shared area, and the two sizes."""
    one, two = Image.open(before).convert("RGB"), Image.open(after).convert("RGB")
    width, height = min(one.width, two.width), min(one.height, two.height)
    one, shown = one.crop((0, 0, width, height)), two.crop((0, 0, width, height))
    moved = ImageChops.difference(one, shown).convert("L").point(lambda value: 255 if value > CHANNEL else 0)
    changed = moved.histogram()[255] / (width * height)
    red = Image.new("RGB", shown.size, (220, 40, 40))
    Image.composite(red, shown, moved).save(picture)
    return changed, (Image.open(before).width, Image.open(before).height), (two.width, two.height)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="var/shots-baseline", type=Path)
    parser.add_argument("--now", default="var/shots", type=Path)
    parser.add_argument("--out", default="var/shots-diff", type=Path)
    parser.add_argument("--only", default="", help="shots whose name contains this")
    options = parser.parse_args()
    options.out.mkdir(parents=True, exist_ok=True)
    names = sorted(path.name for path in options.baseline.glob("*.png") if options.only in path.name)
    print(f"{'shot':28} {'changed':>8}  size")
    for name in names:
        now = options.now / name
        if not now.is_file():
            print(f"{name:28} {'missing':>8}")
            continue
        share, was, is_ = compare(options.baseline / name, now, options.out / name)
        size = f"{was[0]}x{was[1]}" if was == is_ else f"{was[0]}x{was[1]} -> {is_[0]}x{is_[1]}"
        print(f"{name:28} {share:8.2%}  {size}")
