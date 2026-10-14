"""The edge granting a user a role on a tenant."""

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Membership, Tenant


def make_membership(user: BaseUser, tenant: Tenant, *, role: str = Role.OWNER) -> Membership:
    return Membership.objects.grant(user=user, tenant=tenant, role=role)
