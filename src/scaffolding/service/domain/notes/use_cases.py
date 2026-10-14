"""The notes use cases: the only business rules in the sample domain.

A use case is a plain function over the data layer - no HTTP, no argv, no
templates. Every interface (HTTP, CLI, web) calls these; none reimplements them.
"""

from scaffolding.data.models import Note


def create_note(*, tenant: int, title: str, body: str) -> Note:
    """Create a note in the given tenant. The title must not be blank."""
    return Note.objects.create(tenant_id=tenant, title=title.strip(), body=body.strip())


def list_notes(*, tenant: int) -> list[Note]:
    """The tenant's notes, newest first."""
    return list(Note.objects.owned_by(tenant))
