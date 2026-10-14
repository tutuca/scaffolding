"""A note: the sample domain that exercises every layer.

One owned row, two fields. It is the template's proof that a model flows from
`data/` (the row) through `service/` (the use cases) to `interface/` (HTTP, CLI)
and `ui/` (the page) without any layer knowing the others' names.
"""

from django.db import models

from .base import OwnedModel, OwnedQuerySet, TimeStampedModel


class NoteQuerySet(OwnedQuerySet["Note"]):
    # Factories

    def add(self, *, tenant: int, title: str, body: str) -> Note:
        """Create a note in a tenant. The title must not be blank."""
        return self.create(tenant_id=tenant, title=title.strip(), body=body.strip())


# The owned manager, so `OwnedAdmin.get_queryset` and the API viewset's
# `owned_by` narrow to one tenant's rows.
NoteManager = models.Manager.from_queryset(NoteQuerySet)


class Note(OwnedModel, TimeStampedModel):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)

    objects = NoteManager()

    class Meta:
        ordering = ["-updated_on"]
        db_table = "note"

    def __str__(self) -> str:
        return self.title
