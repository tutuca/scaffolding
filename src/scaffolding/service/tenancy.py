"""Which tenant, and whether you may. Every shell asks both, in that order.

Plain functions, not a middleware: a middleware leaves its answer somewhere
ambient, and "the current tenant" as ambient state is invisible in the queries it
shapes and wrong in a management command.
"""

from typing import cast

from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.views import APIView

from scaffolding.data.models import BaseUser, Tenant

# Django's codename pattern, the way DRF spells a permission template.
VIEW_PERMISSION = "%(app_label)s.view_%(model_name)s"


def person(request: Request) -> BaseUser:
    """The person behind this request. Anonymous is already refused upstream."""
    return cast(BaseUser, request.user)


def active_tenant(request: Request) -> Tenant:
    """The tenant this request acts on.

    The user's own column, and no header override: a per-request answer is one an
    authentication backend cannot see. Switching tenants is `BaseUser.look_at`.
    """
    tenant = person(request).active_tenant
    if tenant is None:
        raise NotFound("This account has no tenant yet. Register one first.")
    return tenant


class IsMember(permissions.BasePermission):
    """Authenticated, and a member of the tenant named.

    The whole check for a computed read model that has no table for
    `DjangoModelPermissions` to resolve a codename against.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        return person(request).role_on(active_tenant(request)) is not None


class ResourcePermission(permissions.DjangoModelPermissions):
    """Django's four codenames, answered by `data/backends.RoleBackend`.

    DRF's own class, with one thing changed: it maps GET to no permission at
    all, and here it maps to `view`, because minimal by default means reading is
    a grant like any other. Which rows is settled by the viewset's queryset, so
    another tenant's row is a 404 on a guessed id.
    """

    perms_map = {
        **permissions.DjangoModelPermissions.perms_map,
        "GET": [VIEW_PERMISSION],
        "HEAD": [VIEW_PERMISSION],
        "OPTIONS": [VIEW_PERMISSION],
    }
