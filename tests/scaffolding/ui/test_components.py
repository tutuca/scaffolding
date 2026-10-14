"""A component is a name that three kinds of file may share, and nothing else.

`templates/ui/components/<name>/<name>.html` is the markup a page includes,
`static/ui/components/<name>/<name>.js` and `.css` what dresses and enhances it - any of
them, never none, always named for the directory (`<name>.*`, or `<name>_<part>.*` for the
second template a form's renderer asks for). Markup is the component and the script
and the stylesheet are sprinkled on it (`docs/DESIGN.md`), so a component with only a
stylesheet and a script is allowed (a form's markup is Django's) and one with only markup
is too (an icon). This is the convention, enforced rather than written down.
"""

from pathlib import Path

import pytest

from scaffolding import ui

UI = Path(ui.__file__).parent
ROOTS = {"templates": UI / "templates/ui/components", "static": UI / "static/ui/components"}
ALLOWED = {"templates": {".html"}, "static": {".js", ".css", ".svg"}}


def components() -> list[tuple[str, Path]]:
    return [(kind, path) for kind, root in ROOTS.items() if root.is_dir() for path in sorted(root.iterdir())]


def test_there_are_components_to_check() -> None:
    assert len(components()) >= 4


@pytest.mark.parametrize(("kind", "path"), components(), ids=lambda value: getattr(value, "name", value))
def test_a_component_is_a_directory_whose_files_are_named_for_it(kind: str, path: Path) -> None:
    assert path.is_dir(), f"{path} is a file where a component directory should be"
    files = sorted(path.iterdir())
    assert files, f"{path} is empty"
    for file in files:
        assert file.stem == path.name or file.stem.startswith(f"{path.name}_"), f"{file} should be named {path.name}.*"
        assert file.suffix in ALLOWED[kind], f"{file} is not one of {sorted(ALLOWED[kind])}"


def test_every_component_has_at_least_one_file_of_some_kind() -> None:
    names = {path.name for _, path in components()}
    kinds = {name: sum(1 for kind, path in components() if path.name == name) for name in names}

    assert all(count >= 1 for count in kinds.values())
