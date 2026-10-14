"""The edge between a person and a tenant, carrying what they may do.

A role on an edge, not an attribute of the person: the same person can own one
tenant and only read another.
"""

from django.conf import settings
from django.db import models

from scaffolding.data.enums import Role
from scaffolding.exceptions import DomainRefusal

from .base import TimeStampedModel


class MembershipQuerySet(models.QuerySet["Membership"]):
    # Queries

    def owners(self) -> MembershipQuerySet:
        return self.filter(role=Role.OWNER)

    # Factories

    def grant(
        self,
        *,
        user: models.Model,
        tenant: models.Model,
        role: str,
        invited_by: models.Model | None = None,
    ) -> Membership:
        """Grant or re-grant. Re-granting changes the role; it never duplicates."""
        if role not in Role.values:
            raise DomainRefusal(f"{role!r} no es un rol: {', '.join(Role.values)}.")
        membership, _ = self.update_or_create(
            user=user, tenant=tenant, defaults={"role": role, "invited_by": invited_by}
        )
        return membership


# django-stubs needs the Manager declared outside the model body.
MembershipManager = models.Manager.from_queryset(MembershipQuerySet)


class Membership(TimeStampedModel):
    """One person's standing on one tenant."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    tenant = models.ForeignKey("data.Tenant", on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    objects = MembershipManager()

    class Meta:
        ordering = ["tenant__slug", "user__email"]
        db_table = "membership"
        constraints = [models.UniqueConstraint(fields=["user", "tenant"], name="uniq_membership")]

    # Mutators

    def revoke(self) -> None:
        """Refuses the last owner: a tenant nobody can administer is a tenant
        nobody can rescue."""
        if self.role == Role.OWNER and type(self).objects.filter(tenant=self.tenant).owners().count() == 1:
            raise DomainRefusal(f"Es el último titular de {self.tenant.name}; no se puede revocar.")
        self.delete()

    def __str__(self) -> str:
        return f"{self.user} - {self.get_role_display()} en {self.tenant.name}"
