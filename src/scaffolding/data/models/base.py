from decimal import Decimal
from typing import Literal, Self, TypeVar, overload

from django.db import models
from django.db.models.expressions import Combinable

from scaffolding.exceptions import DomainRefusal
from scaffolding.types import (
    INDEX_DIGITS,
    INDEX_PLACES,
    MONEY_DIGITS,
    MONEY_PLACES,
    PERCENTAGE_DIGITS,
    PERCENTAGE_PLACES,
    RATE_DIGITS,
    RATE_PLACES,
)

# Only an owned model has a taxpayer to scope by.
OwnedRow = TypeVar("OwnedRow", bound="OwnedModel")

# django-stubs parameterises a field as [what you may assign, what you read back].
# Naming the pair keeps the helpers below readable and makes reads Decimal rather
# than untyped, which is what lets model properties do arithmetic on them. Named
# for the shape and not for money, because `rate()` returns one too.
type DecimalColumn = models.DecimalField[Decimal | Combinable, Decimal]
# A nullable column may be assigned None; django-stubs refines its read type to
# include None automatically, so only the assignable side needs naming here.
type OptionalDecimalColumn = models.DecimalField[Decimal | Combinable | None, Decimal | None]


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


@overload
def money(
    max_digits: int = MONEY_DIGITS,
    *,
    null: Literal[True],
    blank: bool = False,
    help_text: str = "",
    verbose_name: str | None = None,
) -> OptionalDecimalColumn: ...


@overload
def money(
    max_digits: int = MONEY_DIGITS,
    *,
    null: Literal[False] = False,
    blank: bool = False,
    help_text: str = "",
    verbose_name: str | None = None,
) -> DecimalColumn: ...


def money(
    max_digits: int = MONEY_DIGITS,
    *,
    null: bool = False,
    blank: bool = False,
    help_text: str = "",
    verbose_name: str | None = None,
) -> DecimalColumn | OptionalDecimalColumn:
    """Money is always Decimal, to the cent. Never float."""
    return models.DecimalField(
        verbose_name,
        max_digits=max_digits,
        decimal_places=MONEY_PLACES,
        null=null,
        blank=blank,
        help_text=help_text,
    )


def rate(*, help_text: str = "") -> DecimalColumn:
    """Exchange rates carry six decimals, matching ARCA's MonCotiz precision."""
    return models.DecimalField(max_digits=RATE_DIGITS, decimal_places=RATE_PLACES, help_text=help_text)


def percentage(*, help_text: str = "") -> DecimalColumn:
    """A published percentage: 4.25 means 4,25%. Four decimals for ARCA's own precision."""
    return models.DecimalField(max_digits=PERCENTAGE_DIGITS, decimal_places=PERCENTAGE_PLACES, help_text=help_text)


def index(*, help_text: str = "") -> DecimalColumn:
    """A published price index: four decimals, the precision INDEC prints."""
    return models.DecimalField(max_digits=INDEX_DIGITS, decimal_places=INDEX_PLACES, help_text=help_text)


class OwnedQuerySet(models.QuerySet[OwnedRow]):
    """`owned_by`, uniformly. Generic over its model rather than a bare mixin: an
    unparameterised base erases the model type down the whole chain."""

    def owned_by(self, taxpayer: int) -> Self:
        """Narrowed to one taxpayer's books, named by id.

        An id and not a row, because this is what an entry point is handed
        (docs/ARCHITECTURE.md, rule 7): each shell answers "which books" its own
        way and only an id is a thing all of them can spell.
        """
        return self.filter(taxpayer_id=taxpayer)


class NarrowedManager[T: "OwnedModel"](models.Manager[T]):
    """A manager whose difference from Django's own is a narrowed `get_queryset`
    plus the `owned_by` forwarder - which the three proxy readings of `Movement`
    each carried verbatim before this class held it once. `get_queryset` must
    return an `OwnedQuerySet`, which is what makes the forwarder typeable. A
    proxy whose narrowed queryset has methods of its own re-declares the
    forwarder so a chained call keeps them (`PaymentManager` does)."""

    def get_queryset(self) -> OwnedQuerySet[T]:
        raise NotImplementedError  # each proxy narrows its own way

    def owned_by(self, taxpayer: int) -> OwnedQuerySet[T]:
        return self.get_queryset().owned_by(taxpayer)


class OwnedModel(models.Model):
    """A row that belongs to one taxpayer's books.

    Every table that is not reference data carries it - no second taxonomy for
    tables whose parent already implies one, which would cost a join in half the
    scoping queries. The duplication cannot drift: a child's taxpayer is never
    an argument, so there is nothing to get wrong.

    PROTECT, not CASCADE: deleting a taxpayer must not delete a ledger.
    """

    taxpayer = models.ForeignKey("data.Taxpayer", on_delete=models.PROTECT, related_name="+")

    class Meta:
        abstract = True


def same_taxpayer(taxpayer: models.Model, **related: OwnedModel | None) -> None:
    """Refuse a related row from different books.

    No constraint can span two tables, so the mutator is the invariant's only
    home. The keyword name is in the message, so a caller learns which argument.
    """
    for name, row in related.items():
        if row is not None and row.taxpayer_id != taxpayer.pk:
            raise DomainRefusal(f"`{name}` pertenece a otro contribuyente.")
