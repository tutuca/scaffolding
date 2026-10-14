"""The notes CLI contract: what argv exposes."""

from io import StringIO

from django.core.management import call_command


def test_add_then_list(tenant) -> None:
    call_command("notes", "add", "--title", "Hello", "--body", "World", "--tenant", tenant.slug)

    out = StringIO()
    call_command("notes", "list", "--tenant", tenant.slug, stdout=out)
    assert "Hello" in out.getvalue()
