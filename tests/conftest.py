from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

import pytest

from scaffolding.data.enums import Role
from scaffolding.data.models import Tenant


@pytest.fixture
def tenant(db: None) -> Tenant:
    """One tenant. Everything a test creates belongs here by default."""
    return Tenant.objects.register(name="Acme")


@pytest.fixture
def other_tenant(db: None) -> Tenant:
    """A second tenant, which must never be visible from the first."""
    return Tenant.objects.register(name="Other")


@pytest.fixture
def user(db: None):
    """A login."""
    return get_user_model().objects.create_user("owner@example.com")


@pytest.fixture
def other_user(db: None):
    """A second login."""
    return get_user_model().objects.create_user("other@example.com")


@pytest.fixture
def owner(user, tenant):
    """`user`, owning `tenant` and looking at it."""
    user.join(tenant, role=Role.OWNER)
    user.look_at(tenant)
    return user


@pytest.fixture
def api(owner) -> APIClient:
    """Authenticated, owning `tenant`, with it active."""
    client = APIClient()
    client.force_login(owner)
    return client


@pytest.fixture
def other_api(other_user, other_tenant) -> APIClient:
    """A second login on a second tenant - the isolation tests' other half."""
    other_user.join(other_tenant, role=Role.OWNER)
    other_user.look_at(other_tenant)
    client = APIClient()
    client.force_login(other_user)
    return client
