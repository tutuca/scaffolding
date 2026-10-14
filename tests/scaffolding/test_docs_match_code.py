"""Two docs enumerate the tree, held to the code the way the architecture rules
are (`test_conventions.py`): ARCHITECTURE's domain list against the packages,
README's command table against the command registry.

Kept deliberately small - the pins that named the whole tree, not the prose
that counts it. A use-case count is the prose that rots; the anchor checks
were tried and dropped as trivial. These two are the claims a reader follows.
"""

import re
from pathlib import Path

from scaffolding.service.commands import COMMANDS

SRC = Path(__file__).resolve().parents[2] / "src" / "scaffolding"
ROOT = SRC.parents[1]

ARCHITECTURE = ROOT / "docs" / "ARCHITECTURE.md"
README = ROOT / "README.md"


def listed_domains() -> set[str]:
    """The `- `name` -` names under ARCHITECTURE's "The domains themselves"."""
    lines = ARCHITECTURE.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line == "The domains themselves:")
    names: set[str] = set()
    for line in lines[start + 1 :]:
        if line.startswith("- "):
            if match := re.match(r"^- `([a-z_]+)` -", line):
                names.add(match.group(1))
            continue
        if line.strip() == "":
            continue
        break
    return names


def domain_packages() -> set[str]:
    """Every domain package under `service/domain/` (a `dates.py` module is not one)."""
    return {p.name for p in (SRC / "service" / "domain").iterdir() if p.is_dir() and p.name != "__pycache__"}


def test_architecture_names_every_domain() -> None:
    """A domain package absent from the list, or named but gone, is drift."""
    listed = listed_domains()
    actual = domain_packages()

    assert listed, "ARCHITECTURE's 'The domains themselves' yielded no `- `name` -` bullets."
    assert listed == actual, (
        f"ARCHITECTURE lists {sorted(listed - actual)} that are not domains, "
        f"and misses {sorted(actual - listed)} that are."
    )


def test_readme_documents_every_command() -> None:
    """The README's command table names every command the CLI exposes."""
    text = README.read_text()
    missing = [name for name, _ in COMMANDS if f"scaffolding {name}" not in text]

    assert not missing, f"README's command table is missing: {missing}."
