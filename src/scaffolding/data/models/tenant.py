"""A tenant: the workspace whose rows are scoped together.

Every owned row points here. A tenant is the unit of isolation - members see only
their own tenant's rows - and the thing a `Membership` grants access to.
"""

from typing import TYPE_CHECKING

from django.db import models
from django.utils.text import slugify

from scaffolding.exceptions import DomainRefusal

from .base import TimeStampedModel
from .membership import Membership

if TYPE_CHECKING:
    from .user import BaseUser


class TenantQuerySet(models.QuerySet["Tenant"]):
    # Factories

    def register(self, *, name: str, slug: str | None = None) -> Tenant:
        """Register a tenant. Refuses a slug already here."""
        key = slug or slugify(name)
        if not key:
            raise DomainRefusal("El nombre no produce un slug válido.")
        if self.filter(slug=key).exists():
            raise DomainRefusal(f"El slug {key!r} ya está en uso.")
        return self.create(name=name, slug=key)


# django-stubs needs the Manager declared outside the model body.
TenantManager = models.Manager.from_queryset(TenantQuerySet)


class Tenant(TimeStampedModel):
    """One tenant's rows."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    objects = TenantManager()

    class Meta:
        ordering = ["slug"]
        db_table = "tenant"

    # Mutators

    def invite(self, user: BaseUser, *, role: str, invited_by: BaseUser | None = None) -> Membership:
        """The other end of `BaseUser.join`; both call the same factory."""
        return Membership.objects.grant(user=user, tenant=self, role=role, invited_by=invited_by)

    def __str__(self) -> str:
        return self.name
