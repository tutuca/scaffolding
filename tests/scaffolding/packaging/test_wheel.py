"""What a wheel ships, pinned exactly.

The wheel is the distribution artifact: everything the tool needs to run on a
machine that has never seen this checkout - the Python modules, the UI's
templates and static, the seeded reference tables, the typing marker - and
nothing else. This file is the guarantee behind that claim, so it is allowed
to be strict in a way no other test is:

- a wheel is built from *committed* source - `git archive HEAD`, never the
  working tree - so a chart mid-edit or a screenshot dropped in `ui/static/`
  cannot leak into what gets installed;
- every committed non-Python file under `src/scaffolding/` must be declared in
  `[tool.setuptools.package-data]` - an asset directory that appears later
  fails here until the declaration names it;
- the metadata's core `Requires-Dist` is exactly `[project.dependencies]`,
  so a debugger cannot slip back into the runtime closure.

The build is `uv build --wheel`, the repo's own tool. Standard library only.
"""

import io
import os
import re
import subprocess
import tarfile
import tomllib
import zipfile
from email import policy
from email.parser import BytesParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

# The non-Python content a wheel may carry: the directories the package-data
# table declares, plus the typing marker. Everything else under src/scaffolding/
# must be a .py module.
DECLARED_NON_PY_PREFIXES = (
    "src/scaffolding/ui/static/",
    "src/scaffolding/ui/templates/",
    "src/scaffolding/data/reference/",
    "src/scaffolding/data/starter/",
)
DIST_INFO_FILES = {"METADATA", "WHEEL", "RECORD", "entry_points.txt", "top_level.txt"}

# Names that exist only inside an optional extra. In the core closure each of
# these is a packaging regression.
EXTRA_ONLY_NAMES = {
    "pytest",
    "pytest-cov",
    "pytest-django",
    "model-bakery",
    "ruff",
    "mypy",
    "django-stubs",
    "djangorestframework-stubs",
    "ipdb",
    "tornado",
    "pillow",
}

FORBIDDEN_PATH_BITS = ("/var/", "/etc/", "/tests/", "/bin/", "__pycache__", ".pyc", ".DS_Store")


@pytest.fixture(scope="session")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The freshly built artifact, once per session.

    Built from `git archive HEAD`, never the working tree: a wheel is an
    artifact of committed source, so an untracked file in the tree - another
    loop's work in progress - cannot leak into what gets installed. The
    `make dist` target builds the same way.
    """
    source = tmp_path_factory.mktemp("source")
    archive = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT, capture_output=True, check=False)
    if archive.returncode != 0:
        pytest.fail("`git archive HEAD` failed; the wheel is built from committed source, so git is required")
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tarball:
        tarball.extractall(source, filter="data")

    out = tmp_path_factory.mktemp("wheel")
    env = {**os.environ, "UV_CACHE_DIR": os.environ.get("UV_CACHE_DIR", str(ROOT / "tmp" / "uv-cache"))}
    result = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(out)],
        cwd=source,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.fail(f"`uv build --wheel` failed:\n{result.stderr}")
    wheels = list(out.glob("*.whl"))
    if len(wheels) != 1:
        pytest.fail(f"expected exactly one wheel, found {wheels}")
    return wheels[0]


def committed_source() -> set[str]:
    """The tracked paths under src/scaffolding/, as git sees them."""
    result = subprocess.run(
        ["git", "ls-files", "src/scaffolding"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.fail("`git ls-files` failed; the wheel is built from committed source, so git is required")
    return {line for line in result.stdout.splitlines() if line}


def dependency_name(spec: str) -> str:
    """`django<7` -> `django`, `django-allauth[socialaccount]` -> `django-allauth`."""
    return re.split(r"[<>=!~;\[( ]", spec, maxsplit=1)[0].strip()


def wheel_paths(wheel: Path) -> set[str]:
    with zipfile.ZipFile(wheel) as archive:
        return set(archive.namelist())


def test_the_wheel_contains_exactly_the_committed_source(wheel: Path) -> None:
    tracked = committed_source()
    expected = {path.removeprefix("src/") for path in tracked if path.endswith(".py")}
    expected |= {
        path.removeprefix("src/")
        for path in tracked
        if not path.endswith(".py") and path.startswith(DECLARED_NON_PY_PREFIXES)
    }
    if "src/scaffolding/py.typed" in tracked:
        expected.add("scaffolding/py.typed")
    actual = wheel_paths(wheel)
    dist_info = {path for path in actual if re.fullmatch(r"scaffolding-[0-9.]+\.dist-info/.*", path)}
    actual = {path for path in actual if path not in dist_info}

    extra = sorted(actual - expected)
    missing = sorted(expected - actual)
    assert not extra, f"in the wheel but not committed: {extra}"
    assert not missing, f"committed but not in the wheel: {missing}"
    assert {Path(path).name for path in dist_info} == DIST_INFO_FILES


def test_every_committed_non_python_file_is_declared_package_data() -> None:
    undeclared = {
        path
        for path in committed_source()
        if not path.endswith(".py")
        and path != "src/scaffolding/py.typed"
        and not path.startswith(DECLARED_NON_PY_PREFIXES)
    }
    assert not undeclared, f"committed non-Python files outside the declared package-data: {sorted(undeclared)}"


def test_metadata_core_dependencies_match_pyproject(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        meta_name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        metadata = BytesParser(policy=policy.default).parsebytes(archive.read(meta_name), headersonly=True)
    requires = metadata.get_all("Requires-Dist") or []

    declared = {dependency_name(spec) for spec in PYPROJECT["project"]["dependencies"]}
    core = {dependency_name(spec) for spec in requires if "; extra ==" not in spec}

    assert core == declared, f"core Requires-Dist drifted from [project.dependencies]: {core} vs {declared}"
    leaked = core & EXTRA_ONLY_NAMES
    assert not leaked, f"a dev name is a core dependency: {leaked}"

    declared_extras = {
        name: {dependency_name(spec) for spec in specs}
        for name, specs in PYPROJECT["project"]["optional-dependencies"].items()
    }
    on_wire: dict[str, set[str]] = {}
    for spec in requires:
        if "; extra ==" in spec:
            group = spec.split("extra ==", 1)[1].strip().strip('"')
            on_wire.setdefault(group, set()).add(dependency_name(spec))
    assert on_wire == declared_extras, (
        f"extras drifted from [project.optional-dependencies]: {on_wire} vs {declared_extras}"
    )


def test_the_entry_point_is_the_one_command(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        entry_name = next(name for name in archive.namelist() if name.endswith(".dist-info/entry_points.txt"))
        entry_points = archive.read(entry_name).decode()
    assert "scaffolding = scaffolding.manage:main" in entry_points
    assert "console_scripts" in entry_points


def test_the_wheel_is_pure_python(wheel: Path) -> None:
    assert "py3-none-any" in wheel.name


def test_no_user_data_or_tooling_in_the_wheel(wheel: Path) -> None:
    offenders = {path for path in wheel_paths(wheel) if any(bit in path for bit in FORBIDDEN_PATH_BITS)}
    assert not offenders, f"user data or tooling in the wheel: {offenders}"
