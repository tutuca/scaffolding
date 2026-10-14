"""The edge between a person and a set of books, carrying what they may do.

Being a contador is a relationship to someone else's books, not something
intrinsic - the same person can be a monotributista and their sister's
accountant. So a role on an edge, not an `AccountantProfile`.

Names both ends by string, so either can import this without a cycle. The person
end was `Profile` until 2026-09-18 and is the login itself now.
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
        taxpayer: models.Model,
        role: str,
        invited_by: models.Model | None = None,
    ) -> Membership:
        """Grant or re-grant. Re-granting changes the role; it never duplicates."""
        if role not in Role.values:
            raise DomainRefusal(f"{role!r} no es un rol: {', '.join(Role.values)}.")
        membership, _ = self.update_or_create(
            user=user, taxpayer=taxpayer, defaults={"role": role, "invited_by": invited_by}
        )
        return membership


# django-stubs needs the Manager declared outside the model body.
MembershipManager = models.Manager.from_queryset(MembershipQuerySet)


class Membership(TimeStampedModel):
    """One person's standing on one taxpayer's books."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    taxpayer = models.ForeignKey("data.Taxpayer", on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    objects = MembershipManager()

    class Meta:
        ordering = ["taxpayer__tax_id", "user__email"]
        db_table = "membership"
        constraints = [models.UniqueConstraint(fields=["user", "taxpayer"], name="uniq_membership")]

    # Mutators

    def revoke(self) -> None:
        """Refuses the last owner: books nobody can administer are books nobody
        can rescue. A constraint compares rows; this counts them."""
        if self.role == Role.OWNER and type(self).objects.filter(taxpayer=self.taxpayer).owners().count() == 1:
            raise DomainRefusal(f"Es el último titular de {self.taxpayer.tax_id}; no se puede revocar.")
        self.delete()

    def __str__(self) -> str:
        return f"{self.user} - {self.get_role_display()} en {self.taxpayer.tax_id}"
