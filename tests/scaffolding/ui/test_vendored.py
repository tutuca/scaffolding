"""The drift alarm: every vendored admin template pinned to its origin.

Owning a template buys its drift; the pin makes the drift loud. When a Django
upgrade moves an origin, the pinned hash stops matching and this fails naming
the file - the ritual is: diff the origin against the previous release,
re-apply what matters to our copy, update the pin. Spec decision 7.
"""

import hashlib
from pathlib import Path

import django
import pytest

from scaffolding import ui

OURS = Path(ui.__file__).parent / "templates" / "admin"
UPSTREAM = Path(django.__file__).parent / "contrib" / "admin" / "templates" / "admin"

# Template -> sha256 of the upstream file it was last merged from.
# Measured 2026-10-06 against Django 6.1's installed tree.
PINNED = {
    "base.html": "3e14f9e1f9cba38186b40ad2c692811ad5e2fb6c652c2bd9d72b14965d46b7e2",
    "base_site.html": "182897817c02fd96758284ca9eb6dd35f58e3688c6c536ad883e610ac03c1d38",
    "change_list.html": "613098bd9f37a1fecf1dd677e1182fc9494d049be4e4be52a256fdcda91ecb30",
    "change_form.html": "147994eac4053c3a633a8fc719d58b47e609f41b98ec47bbdb6adea430674621",
}


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("name", sorted(PINNED))
def test_the_origin_has_not_moved(name: str) -> None:
    assert fingerprint(UPSTREAM / name) == PINNED[name], (
        f"upstream moved: re-diff django's admin/{name} against our copy, then update the pin"
    )


def test_every_shadowing_template_is_pinned() -> None:
    """A vendored file nobody pinned is drift nobody hears."""
    shadowing = {path.name for path in OURS.glob("*.html") if (UPSTREAM / path.name).is_file()}
    assert shadowing == set(PINNED), f"pinned {sorted(PINNED)} but shadowing {sorted(shadowing)}"


# Vendored JavaScript: the chart library and its d3 peer, pinned so a re-download
# that changes bytes fails here instead of drifting. Observable Plot 0.6.17 on
# d3 7.9.0, fetched 2026-10-06 from jsdelivr.
VENDORED_JS = {
    "d3.min.js": "f2094bbf6141b359722c4fe454eb6c4b0f0e42cc10cc7af921fc158fceb86539",
    "plot.umd.min.js": "4358086467740777dd788d6b27a95cebdbaefdd50c730a3060117073bd7134cb",
}
STATIC = Path(ui.__file__).parent / "static" / "ui" / "vendor"


@pytest.mark.parametrize("name", sorted(VENDORED_JS))
def test_vendored_js_is_pinned(name: str) -> None:
    assert fingerprint(STATIC / name) == VENDORED_JS[name], f"{name} moved; re-vendor and update the pin"
