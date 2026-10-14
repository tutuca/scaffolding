"""Which books, and whether you may. Every shell asks both, in that order.

Plain functions, not a middleware: a middleware leaves its answer somewhere
ambient, and "the current taxpayer" as ambient state is invisible in the queries
it shapes and wrong in a management command.

*Whether you may* is no longer answered here. `data/backends.RoleBackend` answers
it, so this file holds DRF's own `DjangoModelPermissions` with one map
overridden - the same `data.change_invoice` string the admin resolves.
"""

from typing import cast

from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.views import APIView

from scaffolding.data.models import BaseUser, Taxpayer

# Django's codename pattern, the way DRF spells a permission template.
VIEW_PERMISSION = "%(app_label)s.view_%(model_name)s"


def person(request: Request) -> BaseUser:
    """The person behind this request. Anonymous is already refused upstream."""
    return cast(BaseUser, request.user)


def active_taxpayer(request: Request) -> Taxpayer:
    """The books this request acts on.

    The profile's own column, and no header override. There was an `X-Taxpayer`
    one until 2026-09-18: nothing sent it, and a per-request answer is one an
    authentication backend cannot see - which is what stopped the admin and the
    API asking the same question. Switching books is `BaseUser.look_at`, which
    refuses any the profile cannot reach.
    """
    books = person(request).active_taxpayer
    if books is None:
        raise NotFound("Esta cuenta todavía no tiene ningún contribuyente. Registrá un CUIT primero.")
    return books


class IsMember(permissions.BasePermission):
    """Authenticated, and a member of the books named.

    The whole check for a computed read model - `tax.position` has no table, so
    `DjangoModelPermissions` has no resource to resolve a codename against.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        return person(request).role_on(active_taxpayer(request)) is not None


class ResourcePermission(permissions.DjangoModelPermissions):
    """Django's four codenames, answered by `data/backends.RoleBackend`.

    DRF's own class, with one thing changed: it maps GET to no permission at
    all, and here it maps to `view`, because minimal by default means reading is
    a grant like any other. Everything else is DRF's - it resolves
    `data.change_invoice` off the view's queryset and calls `user.has_perms`,
    which the backend answers off `data/visibility.py`, from the same table and
    by the same route as the admin.

    Only the resource: which rows is settled by `ScaffoldingModelViewSet.get_queryset`,
    which `get_object` resolves through, so another taxpayer's row is a 404 on a
    guessed id. A second per-object check would be the same answer twice.
    """

    perms_map = {
        **permissions.DjangoModelPermissions.perms_map,
        "GET": [VIEW_PERMISSION],
        "HEAD": [VIEW_PERMISSION],
        "OPTIONS": [VIEW_PERMISSION],
    }
