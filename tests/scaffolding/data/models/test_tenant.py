"""The Tenant contract: registering a workspace and its slug."""

import pytest

from scaffolding.exceptions import DomainRefusal
from tests.recipes.tenant import make_tenant

pytestmark = pytest.mark.django_db


def test_register_derives_the_slug() -> None:
    assert make_tenant(name="Acme Corp").slug == "acme-corp"


def test_register_refuses_a_duplicate_slug() -> None:
    make_tenant(name="Acme")
    with pytest.raises(DomainRefusal):
        make_tenant(name="Acme")
