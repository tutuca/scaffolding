"""What every serializer is built from: the field helpers, and the plain factory.

A wire shape and the column behind it must agree on precision, so both come from
the same constants in `scaffolding.types`.
"""

from typing import cast

from django.db import models
from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework.relations import RelatedField

from scaffolding.data.models.base import OwnedModel, OwnedQuerySet
from scaffolding.types import MONEY_DIGITS, MONEY_PLACES, QUANTITY_DIGITS, RATE_DIGITS, RATE_PLACES

# Never serialized, on any resource: see `plain`.
HIDDEN = ["tenant"]


class OwnedSerializer(serializers.ModelSerializer):
    """A serializer whose relations offer only the request's own books.

    Validation and the browsable API's dropdowns read the same queryset, so
    narrowing it here does both at once: a foreign pk fails as "does not
    exist", the same non-answer a guessed detail URL gets from `get_queryset`.
    Reference relations pass through untouched - the rate table is nobody's.

    Without a request - the schema generator, a stray construction - the
    choices are empty, never everybody's. Failing open here is how a PATCH
    repointed an owned contract at another taxpayer's client on 2026-09-20.
    """

    def get_fields(self) -> dict[str, Field]:
        fields = super().get_fields()
        for field in fields.values():
            # A many=True relation wraps the real one; scope what validates.
            relation = getattr(field, "child_relation", field)
            if not isinstance(relation, RelatedField):
                continue
            queryset = relation.queryset
            if queryset is not None and issubclass(queryset.model, OwnedModel):
                relation.queryset = self.books(cast(OwnedQuerySet[OwnedModel], queryset))
        return fields

    def books(self, queryset: OwnedQuerySet[OwnedModel]) -> OwnedQuerySet[OwnedModel]:
        request = self.context.get("request")
        looking = getattr(request, "user", None)
        active: int | None = getattr(looking, "active_tenant_id", None)
        return queryset.owned_by(active) if active is not None else queryset.none()


def money_field(
    *,
    max_digits: int = MONEY_DIGITS,
    source: str | None = None,
    read_only: bool = False,
    allow_null: bool = False,
) -> serializers.DecimalField:
    """Money on the wire, at the precision `money()` gives it in the database."""
    return serializers.DecimalField(
        max_digits=max_digits,
        decimal_places=MONEY_PLACES,
        source=source,
        read_only=read_only,
        allow_null=allow_null,
    )


def rate_field(
    *, source: str | None = None, read_only: bool = False, allow_null: bool = False
) -> serializers.DecimalField:
    """An exchange rate on the wire, at the precision `rate()` gives it."""
    return serializers.DecimalField(
        max_digits=RATE_DIGITS,
        decimal_places=RATE_PLACES,
        source=source,
        read_only=read_only,
        allow_null=allow_null,
    )


def quantity_field() -> serializers.DecimalField:
    """An invoice line's quantity, matching `InvoiceLine.quantity`."""
    return serializers.DecimalField(max_digits=QUANTITY_DIGITS, decimal_places=MONEY_PLACES)


def plain(model: type[models.Model]) -> type[serializers.ModelSerializer]:
    """A serializer that says nothing but "this model, every field".

    Nine of them existed as nine files differing by a noun. The architecture's
    "one class per file" carries the clause "unless trivial", and these are the
    trivial case: a table of models beats nine copies of the same four lines.

    A resource whose wire shape carries a rule - `Account` hiding the bank
    identifiers, `Invoice` freezing what ARCA owns - keeps its own module, because
    that rule is the thing worth reading.

    `taxpayer` is never on the wire. Which books a write lands in comes from the
    request, so a client that could name the field could write into someone
    else's. `perform_create` would refuse it anyway; the field has no business
    being offered.
    """
    # Reference models have no taxpayer to hide, and DRF refuses to exclude a
    # field that is not there - so the split between owned and reference data
    # decides the shape here too.
    columns = {field.name for field in model._meta.get_fields()}
    hidden = [name for name in HIDDEN if name in columns]
    shape = {"exclude": hidden} if hidden else {"fields": "__all__"}
    return type(
        f"{model.__name__}Serializer",
        (OwnedSerializer,),
        {"Meta": type("Meta", (), {"model": model, **shape})},
    )
