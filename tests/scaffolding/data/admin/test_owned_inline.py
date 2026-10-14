"""An inline row belongs to its parent's books, and cannot be told otherwise."""

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.test import Client, RequestFactory
from django.urls import reverse

from scaffolding.data.admin.invoice import InvoiceAdmin, InvoiceLineInline
from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Taxpayer
from scaffolding.data.models.invoice import Invoice
from scaffolding.data.models.invoice_line import InvoiceLine
from tests.recipes.base import Maker

pytestmark = pytest.mark.django_db


@pytest.fixture
def root(db: None, taxpayer: Taxpayer) -> BaseUser:
    """A superuser is the only one the inline renders for: InlineModelAdmin asks
    the global permission, which TaxpayerBackend declines for everybody else."""
    account = get_user_model().objects.create_superuser("root@example.com", "x")
    account.join(taxpayer, role=Role.OWNER)
    account.look_at(taxpayer)
    return account


def test_the_form_does_not_offer_a_taxpayer(rf: RequestFactory, root: BaseUser, other_taxpayer: Taxpayer) -> None:
    """It used to, as a select listing every taxpayer in the install."""
    request = rf.get("/")
    request.user = root

    assert "taxpayer" not in InvoiceLineInline(Invoice, admin.site).get_formset(request).form.base_fields


def test_a_line_added_in_the_admin_lands_in_the_scaffolding_books(
    client: Client, rf: RequestFactory, root: BaseUser, make_invoice: Maker[Invoice], other_taxpayer: Taxpayer
) -> None:
    """The dropdown is gone, so the row takes its books from the parent."""
    invoice = make_invoice()
    request = rf.get("/")
    request.user = root
    editable = InvoiceAdmin(Invoice, admin.site).get_form(request, invoice)(instance=invoice)
    fields = model_to_dict(invoice, fields=list(editable.fields))
    client.force_login(root)

    response = client.post(
        reverse("admin:data_invoice_change", args=[invoice.pk]),
        {
            **{name: "" if value is None else str(value) for name, value in fields.items()},
            "lines-TOTAL_FORMS": "1",
            "lines-INITIAL_FORMS": "0",
            "lines-MIN_NUM_FORMS": "0",
            "lines-MAX_NUM_FORMS": "1000",
            "lines-0-description": "Consultoría",
            "lines-0-quantity": "2",
            "lines-0-unit_price": "150",
        },
    )

    assert response.status_code == 302, response.context_data["errors"] if response.context_data else response
    line = InvoiceLine.objects.get(invoice=invoice)
    assert line.taxpayer_id == invoice.taxpayer_id
    assert line.taxpayer_id != other_taxpayer.pk
