"""The plain admins: one row of config per model, registered from one table.

A model whose whole body is `list_display` plus a filter is a row, not a file
(ARCHITECTURE, "Data, not hierarchy"). Admins with behaviour of their own keep
their file beside this one.
"""

from django.contrib import admin

from ..models.note import Note
from .base import OwnedAdmin

# (model, base, attributes)
PLAIN: list[tuple[type, type[admin.ModelAdmin], dict[str, object]]] = [
    (Note, OwnedAdmin, {"list_display": ("title", "updated_on"), "search_fields": ("title", "body")}),
]


def register() -> None:
    """One `ModelAdmin` per row, built from its config."""
    for model, base, config in PLAIN:
        admin.site.register(model, type(f"{model.__name__}Admin", (base,), config))
