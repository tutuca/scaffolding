"""The Membership contract: granting a role, and refusing to orphan a tenant."""

import pytest

from scaffolding.data.enums import Role
from scaffolding.exceptions import DomainRefusal
from tests.recipes.membership import make_membership
from tests.recipes.tenant import make_tenant
from tests.recipes.user import make_user

pytestmark = pytest.mark.django_db


def test_grant_sets_the_role() -> None:
    membership = make_membership(user=make_user(), tenant=make_tenant(), role=Role.OWNER)
    assert membership.role == Role.OWNER


def test_revoke_refuses_the_last_owner() -> None:
    membership = make_membership(user=make_user(), tenant=make_tenant(), role=Role.OWNER)
    with pytest.raises(DomainRefusal):
        membership.revoke()
