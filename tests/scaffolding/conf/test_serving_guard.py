"""The SECRET_KEY default: blocked at serve time, listed at deploy time.

A fresh install runs with a known default key so the suite and a local shell
work unconfigured. That default must never answer the network - sessions
would be forgeable - so `manage.py` refuses `runserver` on it unless DEBUG is
on, and `data/checks.py` names it under `check --deploy`. The refusal is the
enforcement; the check is the same rule where a deploy checklist reads it.
"""

import pytest
from django.core.checks import Tags, run_checks
from django.core.management.base import CommandError
from django.test import override_settings

from scaffolding.conf.serving import refuse_insecure_key
from scaffolding.conf.settings import INSECURE_SECRET_KEY


@override_settings(DEBUG=False, SECRET_KEY=INSECURE_SECRET_KEY)
def test_serving_with_the_insecure_default_key_is_refused() -> None:
    with pytest.raises(CommandError, match="SECRET_KEY"):
        refuse_insecure_key()


@override_settings(DEBUG=False, SECRET_KEY="a-real-key")
def test_serving_with_a_real_key_is_allowed() -> None:
    refuse_insecure_key()


@override_settings(DEBUG=True, SECRET_KEY=INSECURE_SECRET_KEY)
def test_local_development_may_serve_with_the_default() -> None:
    refuse_insecure_key()


@override_settings(DEBUG=False, SECRET_KEY=INSECURE_SECRET_KEY)
def test_the_deploy_check_names_the_insecure_default_key() -> None:
    checks = run_checks(include_deployment_checks=True, tags=[Tags.security])

    assert any(check.id == "scaffolding.security.W001" for check in checks)


@override_settings(DEBUG=False, SECRET_KEY="a-real-key")
def test_the_deploy_check_is_silent_with_a_real_key() -> None:
    checks = run_checks(include_deployment_checks=True, tags=[Tags.security])

    assert not any(check.id == "scaffolding.security.W001" for check in checks)
