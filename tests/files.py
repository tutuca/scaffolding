"""Where the recorded answers live. Resolved once, so no test counts `parents[]`."""

from pathlib import Path

RECORDINGS = Path(__file__).resolve().parent / "recordings"
WSFEX = RECORDINGS / "wsfex"
PAYONEER = RECORDINGS / "payoneer"
PADRON = RECORDINGS / "padron"
INDEC = RECORDINGS / "indec"
BCRA = RECORDINGS / "bcra"
MIRROR = RECORDINGS / "mirror"


def wsfex(name: str) -> str:
    """One recorded ARCA envelope, as text."""
    return (WSFEX / name).read_text()


def padron(name: str) -> str:
    """One padrón constancia answer, as text. Provisional until the probe records it."""
    return (PADRON / name).read_text()


def indec(name: str) -> str:
    """One recorded INDEC table, as text. The CSVs as the site served them."""
    return (INDEC / name).read_text()


def bcra(name: str) -> str:
    """One recorded BCRA series answer, as text."""
    return (BCRA / name).read_text()


def mirror(name: str) -> str:
    """One recorded mirror page, as text."""
    return (MIRROR / name).read_text()
