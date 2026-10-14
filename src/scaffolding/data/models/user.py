"""A login, and the person behind it.

Email is the identifier because Google is the only gateway. `active_taxpayer` -
"which books am I looking at" - is a preference rather than an authentication
fact, and it sits here for the same reason Django's own `AbstractUser` carries a
name: a one-to-one side table for three columns is a join on every request.

There was one, `Profile`, until 2026-09-18. Its argument was that swapping an
auth model is the expensive operation this design avoids doing twice, so the
auth table should have few reasons to change - but that swap already happened in
`0001`, where `AUTH_USER_MODEL` became `data.BaseUser`. What stays split is the
part that earns it: `Taxpayer` is identity in ARCA, and `Membership` is the edge
carrying the role.
"""

from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from scaffolding.data.enums import Role
from scaffolding.exceptions import DomainRefusal

from .base import TimeStampedModel
from .membership import Membership
from .taxpayer import Taxpayer


class UserQuerySet(models.QuerySet["BaseUser"]):
    # Factories

    def create_user(self, email: str, password: str | None = None, **extra: object) -> BaseUser:
        """The one way a user is made. A Google signup passes no password."""
        if not email:
            raise ValueError("A user needs an email: it is the identifier.")
        user = self.model(email=BaseUserManager.normalize_email(email), **extra)
        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra: object) -> BaseUser:
        """The one way in that skips the gateway.

        It used to make the `Profile` the gateway would have made, so that
        "every account has a profile" held on both paths. With the person on
        this row there is no second thing to create and no path to forget it.
        """
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


# django-stubs needs the Manager declared outside the model body.
UserManager = models.Manager.from_queryset(UserQuerySet)


class BaseUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """One account, and the person holding it.

    `is_staff` opens the admin; `is_superuser` sees everything and bypasses
    `data/backends.RoleBackend` entirely, which is what makes that distinction
    load-bearing.
    """

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # SET_NULL: losing access to books must not delete the person.
    active_taxpayer = models.ForeignKey(
        "data.Taxpayer", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    USERNAME_FIELD = "email"
    # ClassVar to match django-stubs' declaration on AbstractBaseUser.
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    objects = UserManager()

    class Meta:
        ordering = ["email"]
        db_table = "user"

    def __str__(self) -> str:
        return self.full_name or self.email

    # Mutators

    def open_admin(self) -> None:
        """Idempotent: signing in twice must not write on the second time."""
        if not self.is_staff:
            self.is_staff = True
            self.save(update_fields=["is_staff"])

    def record_name(self, full_name: str) -> None:
        """What Google said this person is called. Idempotent, and it never
        blanks a name with an empty one: signing in again must not erase it."""
        if full_name and full_name != self.full_name:
            self.full_name = full_name
            self.save(update_fields=["full_name", "updated_on"])

    def join(self, taxpayer: Taxpayer, *, role: str, invited_by: BaseUser | None = None) -> Membership:
        """One end of the edge; `Taxpayer.invite` is the other. Same factory."""
        return Membership.objects.grant(user=self, taxpayer=taxpayer, role=role, invited_by=invited_by)

    def look_at(self, taxpayer: Taxpayer) -> None:
        """Switch the active books, refusing any this account cannot reach."""
        if not self.memberships.filter(taxpayer=taxpayer).exists():
            raise DomainRefusal(f"No tenés acceso al contribuyente {taxpayer.tax_id}.")
        self.active_taxpayer = taxpayer
        self.save(update_fields=["active_taxpayer", "updated_on"])

    # Queries

    def taxpayers(self) -> models.QuerySet[Taxpayer]:
        """Every set of books this account can reach, in any role."""
        return Taxpayer.objects.filter(memberships__user=self).order_by("tax_id")

    def role_on(self, taxpayer: Taxpayer) -> str | None:
        """The role, or None."""
        membership = self.memberships.filter(taxpayer=taxpayer).first()
        return membership.role if membership else None

    def may_write(self, taxpayer: Taxpayer) -> bool:
        return self.role_on(taxpayer) in {Role.OWNER, Role.ACCOUNTANT}

    def may_administer(self, taxpayer: Taxpayer) -> bool:
        """Certificates and memberships. Using a credential is not managing it."""
        return self.role_on(taxpayer) == Role.OWNER
