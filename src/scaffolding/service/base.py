"""What every viewset is built from: the refusal mapping, and the CRUD factory."""

from typing import cast

from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from scaffolding.data import serializers
from scaffolding.data.models.base import OwnedModel, OwnedQuerySet
from scaffolding.exceptions import DomainRefusal
from scaffolding.service.tenancy import ResourcePermission, active_tenant


class ScaffoldingModelViewSet(viewsets.ModelViewSet):
    """Adds one thing to ModelViewSet: a refused write answers 400, not 500.

    Mapping it here keeps the viewsets free of repeated try/except blocks, and
    keeps the rules themselves in the domain, where they are testable without
    HTTP. `DomainRefusal` is what the domain raises; `ValidationError` is what a
    model mutator raises for a value wrong on its own terms, and DRF does not
    handle Django's own exception.
    """

    permission_classes = [ResourcePermission]

    def get_queryset(self) -> models.QuerySet:
        """Narrowed to the books this request names, where there are books.

        The one place it happens for every resource: `crud()` builds twelve
        viewsets on this class, and a per-viewset override would be twelve
        chances to forget.

        Six of those twelve are reference tables, which carry no taxpayer -
        a per-CUIT copy of the monotributo scale would be a per-CUIT copy of the
        law. Narrowing them is not merely unnecessary, it raises: their querysets
        have no `owned_by`, so `GET /monotributo/scale/` answered 500 to every
        member until 2026-09-18. Nothing noticed, because no test had ever
        fetched a reference resource over HTTP.

        Reading them needs no narrowing and writing them is refused a row above:
        `data/visibility.py` grants every role `view` on reference data and
        nothing else, so `perform_create` is unreachable for these.
        """
        queryset = super().get_queryset()
        if not issubclass(queryset.model, OwnedModel):
            return queryset
        # Cast rather than a narrower base: DRF types `get_queryset` against the
        # unparameterised QuerySet, and what is left here is owned.
        return cast(OwnedQuerySet, queryset).owned_by(self.tenant)

    @property
    def tenant(self) -> int:
        """Which tenant this request acts on, as the id an entry point takes."""
        return active_tenant(self.request).pk

    def perform_create(self, serializer: BaseSerializer) -> None:
        """The tenant comes from the request, never from the payload: a client
        that could name it could write into another tenant's rows. No serializer
        carries the field either, so there are two reasons it cannot be chosen
        and neither depends on the other."""
        serializer.save(tenant=active_tenant(self.request))

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, DomainRefusal):
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(exc, ValidationError):
            return Response({"detail": "; ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)


def crud(model: type[models.Model]) -> type[ScaffoldingModelViewSet]:
    """The viewset for a resource with no rules of its own: list, read, write.

    Eleven of these existed as eleven files differing by a noun - the same "unless
    trivial" clause that collapsed the plain serializers. A resource that does
    something (`Payment.unmatched`, `Invoice.portal_sheet`) keeps its own module,
    because the `@action` is the thing worth reading.
    """
    return type(
        f"{model.__name__}ViewSet",
        (ScaffoldingModelViewSet,),
        {"queryset": model._default_manager.all(), "serializer_class": serializers.of(model)},
    )
