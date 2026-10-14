"""A login, and the person behind it.

Email is the identifier. `active_tenant` - "which tenant am I looking at" - is a
preference rather than an authentication fact, and it sits here for the same
reason Django's own `AbstractUser` carries a name: a one-to-one side table for
one column is a join on every request.
"""

from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from scaffolding.data.enums import Role
from scaffolding.exceptions import DomainRefusal

from .base import TimeStampedModel
from .membership import Membership
from .tenant import Tenant


class UserQuerySet(models.QuerySet["BaseUser"]):
    # Factories

    def create_user(self, email: str, password: str | None = None, **extra: object) -> BaseUser:
        """The one way a user is made."""
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
        """The one way in that skips the gateway."""
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


# django-stubs needs the Manager declared outside the model body.
UserManager = BaseUserManager.from_queryset(UserQuerySet)


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

    # SET_NULL: losing access to a tenant must not delete the person.
    active_tenant = models.ForeignKey("data.Tenant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

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
        """What the login said this person is called. Idempotent, and it never
        blanks a name with an empty one."""
        if full_name and full_name != self.full_name:
            self.full_name = full_name
            self.save(update_fields=["full_name", "updated_on"])

    def join(self, tenant: Tenant, *, role: str, invited_by: BaseUser | None = None) -> Membership:
        """One end of the edge; `Tenant.invite` is the other. Same factory."""
        return Membership.objects.grant(user=self, tenant=tenant, role=role, invited_by=invited_by)

    def look_at(self, tenant: Tenant) -> None:
        """Switch the active tenant, refusing any this account cannot reach."""
        if not self.memberships.filter(tenant=tenant).exists():
            raise DomainRefusal(f"No tenés acceso a {tenant.name}.")
        self.active_tenant = tenant
        self.save(update_fields=["active_tenant", "updated_on"])

    # Queries

    def tenants(self) -> models.QuerySet[Tenant]:
        """Every tenant this account can reach, in any role."""
        return Tenant.objects.filter(memberships__user=self).order_by("slug")

    def role_on(self, tenant: Tenant) -> str | None:
        """The role, or None."""
        membership = self.memberships.filter(tenant=tenant).first()
        return membership.role if membership else None

    def may_write(self, tenant: Tenant) -> bool:
        return self.role_on(tenant) in {Role.OWNER, Role.EDITOR}

    def may_administer(self, tenant: Tenant) -> bool:
        """Memberships. Using access is not managing it."""
        return self.role_on(tenant) == Role.OWNER
