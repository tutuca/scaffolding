from typing import Protocol

import pytest
from django.core.management import call_command
from django.tasks import Task, TaskResult
from rest_framework.test import APIClient

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Tenant
from tests.recipes.membership import make_membership
from tests.recipes.tenant import make_tenant
from tests.recipes.user import make_user


@pytest.fixture
def tenant(db: None) -> Tenant:
    """One tenant. Everything a test creates belongs here by default."""
    return make_tenant(name="Acme")


@pytest.fixture
def other_tenant(db: None) -> Tenant:
    """A second tenant, which must never be visible from the first."""
    return make_tenant(name="Other")


@pytest.fixture
def user(db: None) -> BaseUser:
    """A login."""
    return make_user(email="owner@example.com")


@pytest.fixture
def other_user(db: None) -> BaseUser:
    """A second login."""
    return make_user(email="other@example.com")


@pytest.fixture
def owner(user: BaseUser, tenant: Tenant) -> BaseUser:
    """`user`, owning `tenant` and looking at it."""
    make_membership(user=user, tenant=tenant, role=Role.OWNER)
    user.look_at(tenant)
    return user


@pytest.fixture
def viewer(db: None, tenant: Tenant) -> BaseUser:
    """A read-only member, looking at `tenant`."""
    person = make_user(email="viewer@example.com")
    make_membership(user=person, tenant=tenant, role=Role.VIEWER)
    person.look_at(tenant)
    return person


@pytest.fixture
def api(owner: BaseUser) -> APIClient:
    """Authenticated, owning `tenant`, with it active."""
    client = APIClient()
    client.force_login(owner)
    return client


@pytest.fixture
def viewer_api(viewer: BaseUser) -> APIClient:
    """Authenticated as a read-only member."""
    client = APIClient()
    client.force_login(viewer)
    return client


class RunTask(Protocol):
    """`run_task`: enqueue a task, drain one worker pass, return the final result."""

    def __call__(self, task: Task, *args: object, **kwargs: object) -> TaskResult: ...


@pytest.fixture
def run_task() -> RunTask:
    """Enqueue a task, drain one worker pass, and return its final result.

    The database backend queues instead of running; this fixture is the test's
    worker. One `db_worker --batch` pass drains whatever was enqueued.
    """

    def _run(task: Task, *args: object, **kwargs: object) -> TaskResult:
        result = task.enqueue(*args, **kwargs)
        call_command("db_worker", batch=True, verbosity=0)
        return task.get_result(result.id)

    return _run


@pytest.fixture
def other_api(other_user: BaseUser, other_tenant: Tenant) -> APIClient:
    """A second login on a second tenant - the isolation tests' other half."""
    make_membership(user=other_user, tenant=other_tenant, role=Role.OWNER)
    other_user.look_at(other_tenant)
    client = APIClient()
    client.force_login(other_user)
    return client
