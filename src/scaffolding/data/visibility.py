"""What each role may do, per resource.

Django's own vocabulary - the four actions it makes a `Permission` row for -
resolved against the membership instead of `user.user_permissions`, because the
answer depends on which tenant the row is in.

Minimal by default: a resource absent from a role's row is invisible to it, and
`test_conventions.py` fails until a new model is classified.
"""

from scaffolding.data.enums import Role

# Django's four, named so the codenames line up: `data.change_note`.
VIEW, ADD, CHANGE, DELETE = "view", "add", "change", "delete"

READ = frozenset({VIEW})
WRITE = frozenset({VIEW, ADD, CHANGE, DELETE})

# A grant on the root carries to what it contains: a line's resource maps back to
# its parent. The sample domain has no child tables, so this is empty.
CONTAINED_BY: dict[str, str] = {}

# Public facts readable by every member and written by no role. Empty until a
# reference table is introduced.
REFERENCE: set[str] = set()

VISIBILITY: dict[str, dict[str, frozenset[str]]] = {
    Role.OWNER: {
        "note": WRITE,
        # The tenant itself, and who else may act on it.
        "tenant": frozenset({VIEW, CHANGE}),
        "membership": WRITE,
    },
    Role.EDITOR: {
        "note": WRITE,
        "tenant": READ,
    },
    Role.VIEWER: {
        "note": READ,
        "tenant": READ,
    },
}


def root_of(model_name: str) -> str:
    """The resource a grant is written against."""
    return CONTAINED_BY.get(model_name, model_name)


def allows(role: str | None, model_name: str, action: str) -> bool:
    """Whether `role` may take `action` on `model_name`. No role allows nothing."""
    if role is None:
        return False
    resource = root_of(model_name)
    if resource in REFERENCE:
        return action in READ
    return action in VISIBILITY.get(role, {}).get(resource, frozenset())
