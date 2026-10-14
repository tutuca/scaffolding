from scaffolding.data.models import Note


def test_note_belongs_to_a_tenant(tenant) -> None:
    note = Note.objects.create(tenant=tenant, title="Hello", body="World")
    assert note.tenant_id == tenant.pk
    assert str(note) == "Hello"


def test_owned_by_narrows_to_one_tenant(tenant, other_tenant) -> None:
    Note.objects.create(tenant=tenant, title="mine")
    Note.objects.create(tenant=other_tenant, title="theirs")

    assert [n.title for n in Note.objects.owned_by(tenant.pk)] == ["mine"]
