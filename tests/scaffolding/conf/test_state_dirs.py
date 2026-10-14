"""Where state lives: the repo layout in a checkout, the env vars in a wheel.

`VAR_DIR` and `SECRETS_DIR` default to the checkout's layout, which is what a
checkout wants. An installed wheel is a different machine shape: `__file__`
sits inside site-packages, so the defaults would write the SQLite ledger, the
ticket caches and the uploaded keys into the install directory - and an
upgrade would wipe them. `SCAFFOLDING_VAR_DIR` and `SCAFFOLDING_SECRETS_DIR` say
where instead, and `make dist`'s smoke install exercises exactly this path.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from django.conf import settings

ROOT = Path(__file__).resolve().parents[3]

REPO_DEFAULTS = [
    ("SCAFFOLDING_VAR_DIR", "VAR_DIR", ROOT / "var"),
    ("SCAFFOLDING_SECRETS_DIR", "SECRETS_DIR", ROOT / "etc" / "secrets"),
]


def test_state_dirs_default_to_the_repo_layout() -> None:
    assert settings.VAR_DIR == ROOT / "var"
    assert settings.SECRETS_DIR == ROOT / "etc" / "secrets"


@pytest.mark.parametrize(("env_name", "attribute", "repo_default"), REPO_DEFAULTS)
def test_the_env_var_moves_the_state(tmp_path: Path, env_name: str, attribute: str, repo_default: Path) -> None:
    moved = tmp_path / "moved"
    result = subprocess.run(
        [sys.executable, "-c", f"from scaffolding.conf import settings; print(settings.{attribute})"],
        cwd=ROOT,
        env={**os.environ, env_name: str(moved)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(moved)


@pytest.mark.parametrize(("env_name", "attribute", "repo_default"), REPO_DEFAULTS)
def test_the_child_falls_back_to_the_repo_layout_when_untold(env_name: str, attribute: str, repo_default: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-c", f"from scaffolding.conf import settings; print(settings.{attribute})"],
        cwd=ROOT,
        env={key: value for key, value in os.environ.items() if key != env_name},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(repo_default)
