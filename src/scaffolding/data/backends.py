"""What a role may do, where Django already asks.

`ModelBackend` answers from `user_permissions` and `groups`, which are global and
static; the answer here depends on which books the person is looking at. So this
backend answers Django's own two questions off `data/visibility.py`, and every
default asker starts working with no override - `ModelAdmin.has_*_permission`,
`{% if perms.data.add_invoice %}` in a template, DRF's `DjangoModelPermissions`.
One table, one reader, and no shell that can drift from another.

**No object, deliberately.** The role is one value per request, and *which rows*
is settled by `get_queryset`, which `ModelAdmin.get_object` and DRF's
`get_object` both resolve through - so another taxpayer's row is a 404 on a
guessed id before anything is asked. A per-object check here would be a second
answer to a settled question, and two answers can drift.

**A superuser never reaches this.** `PermissionsMixin.has_perm` and
`.has_module_perms` both return True for one *before* consulting any backend.
That is what `4287167` had backwards when it deleted `TaxpayerBackend` on the
grounds that a backend must decline the global question to leave superusers to
`ModelBackend`. The empty admin index it was fixing had a different cause:
`has_module_perms` was never implemented, and `_user_has_module_perms` is an
`any()` over the backends, so `ModelBackend` answered alone - and a Google
signup has no `Permission` rows.
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser
from django.db import models

from scaffolding.data.models import BaseUser
from scaffolding.data.visibility import VISIBILITY, allows

# The one app whose tables `data/visibility.py` classifies. Asked about any
# other - `auth`, `socialaccount`, `admin` - this backend declines, so those
# pages stay reachable by a superuser or not at all.
APP_LABEL = "data"


class RoleBackend(BaseBackend):
    """Grants what the membership allows on the books being looked at."""

    def role(self, user: BaseUser | AnonymousUser) -> str | None:
        """The person's role on their active books, or None.

        None for a stranger and for a closed account, because this is asked on
        pages Django renders before anybody has logged in: `AdminSite.login`
        builds the whole app list through `each_context`.
        """
        if isinstance(user, AnonymousUser) or not user.is_active or user.active_taxpayer is None:
            return None
        return user.role_on(user.active_taxpayer)

    def has_perm(self, user_obj: BaseUser | AnonymousUser, perm: str, obj: models.Model | None = None) -> bool:
        """`data.change_invoice` -> the table, split the way Django spells it."""
        app_label, _, codename = perm.partition(".")
        action, _, model_name = codename.partition("_")
        return app_label == APP_LABEL and allows(self.role(user_obj), model_name, action)

    def has_module_perms(self, user_obj: BaseUser | AnonymousUser, app_label: str) -> bool:
        """What `ModelAdmin.has_module_permission` asks first, and what drops the
        whole app from the index when nobody answers it."""
        return app_label == APP_LABEL and bool(VISIBILITY.get(self.role(user_obj) or "", {}))
