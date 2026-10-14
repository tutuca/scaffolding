from scaffolding.data.models import Tenant
from scaffolding.service.domain.notes import use_cases


def test_create_and_list_notes(tenant: Tenant) -> None:
    use_cases.create_note(tenant=tenant.pk, title="Hello", body="World")

    notes = use_cases.list_notes(tenant=tenant.pk)
    assert [n.title for n in notes] == ["Hello"]


def test_notes_are_scoped_per_tenant(tenant: Tenant, other_tenant: Tenant) -> None:
    use_cases.create_note(tenant=tenant.pk, title="mine", body="")
    use_cases.create_note(tenant=other_tenant.pk, title="theirs", body="")

    assert [n.title for n in use_cases.list_notes(tenant=tenant.pk)] == ["mine"]
