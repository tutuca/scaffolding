"""A note in a tenant, through the model's own factory."""

from model_bakery.recipe import Recipe

from scaffolding.data.models import Note, Tenant

note = Recipe(Note, title="A note")


def make_note(tenant: Tenant, *, title: str = "A note", body: str = "") -> Note:
    return Note.objects.add(tenant=tenant.pk, title=title, body=body)
