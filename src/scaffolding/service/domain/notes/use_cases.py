"""The notes use cases: the only business rules in the sample domain.

A use case is a plain function over the data layer - no HTTP, no argv, no
templates. Every interface (HTTP, CLI, web) calls these; none reimplements them.
Writes go through the model's own factory (`Note.objects.add`), never a raw
`create`, so the model owns its table (docs/ARCHITECTURE.md).
"""

from scaffolding.data.models import Note


def create_note(*, tenant: int, title: str, body: str) -> Note:
    """Create a note in the given tenant. The title must not be blank."""
    return Note.objects.add(tenant=tenant, title=title, body=body)


def list_notes(*, tenant: int) -> list[Note]:
    """The tenant's notes, newest first."""
    return list(Note.objects.owned_by(tenant))
