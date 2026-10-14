"""Vocabulary shared by every layer. Imports nothing from the project.

The precisions live here rather than in `data/models/base.py` because a column
and the wire shape that carries it have to agree, and because the pure core
(`calc.py`) quantizes with them and must not reach into the ORM for them. The
comprobante label is here for the same reason: the ledger, the journal and the
report all name a comprobante, and they have to name it identically or the
reconciliation matches nothing.
"""

from dataclasses import dataclass
from decimal import Context, Decimal
from typing import Literal, Self

# Money is exact to the cent, never a float.
MONEY_DIGITS, MONEY_PLACES = 14, 2
# The rolling twelve-month total and the scale's caps outgrow fourteen digits.
LARGE_MONEY_DIGITS = 16
# Exchange rates carry six decimals, matching ARCA's MonCotiz precision.
RATE_DIGITS, RATE_PLACES = 12, 6
QUANTITY_DIGITS = 10
# A published percentage (4.25 is 4,25%) and a published price index, each at the
# precision its publisher prints.
PERCENTAGE_DIGITS, PERCENTAGE_PLACES = 6, 4
INDEX_DIGITS, INDEX_PLACES = 14, 4
# The one quartile convention the figures share: `statistics.quantiles`' inclusive
# reading, so a band over two months never reaches outside what was observed.
QUANTILE_METHOD: Literal["inclusive", "exclusive"] = "inclusive"

# The calendar, as definitions rather than assumptions: a year is twelve months
# and, on the act/365 convention every peso deposit here is quoted on, 365 days.
# Named once so no formula carries a bare 12 or 365.
MONTHS_PER_YEAR = 12
DAYS_PER_YEAR = 365
WEEKS_PER_YEAR = 52
# The look-back of the figures that *show* a stretch of time - the home's flows, the
# weekly telescope: half a year of months, or of weeks.
HALF_YEAR_MONTHS = MONTHS_PER_YEAR // 2
HALF_YEAR_WEEKS = WEEKS_PER_YEAR // 2
# The one window every reading of *habit* uses - the baseline, the run rate, what
# recurs and what does not, the cut stack, the projection, the runway - so a number
# on one chart is the number on the next. Six closed months, and not fewer: it also
# decides what "sparse" means - seen in fewer than half of them - and in three months
# a habit that missed one month (the groceries, the therapist, a subscription) is
# "seen once" and reads as something that does not come back. Changing it moves the
# headline, not just a figure; see docs/BUDGET.md.
BASELINE_MONTHS = HALF_YEAR_MONTHS

# The quantize targets, derived so a precision is stated once.
CENT = Decimal(1).scaleb(-MONEY_PLACES)
RATE_QUANTUM = Decimal(1).scaleb(-RATE_PLACES)


class Rate(Decimal):
    """A fraction of one whose period is part of the type: `0.23` is 23%, and the
    subclass says whether that is a year, a month, a day or a term.

    The period is part of the type because Argentine rates punish conflating them:
    23% a year is not the 1.9% a month it works out to, and a TNA is not a TEA.
    mypy refuses to hand a `Monthly` to a function that wants an `Annual`.

    Arithmetic keeps the period. `Annual + Annual` is an `Annual`, `1 + monthly`
    a `Monthly`, `(1 + annual) ** 12 - 1` still an `Annual`, and rounding it does
    not shed it. Multiplication is deliberately left as plain `Decimal`: money
    times a rate is money, and a rate scaled by a factor is written as division
    (`rate / 2`). The period changes only where `savings.calc` converts -
    `monthly(Annual) -> Monthly` and its inverse `compound_annual`,
    `daily(Nominal) -> Daily`, and so on.
    """

    def __add__(self, other: Decimal | int, /) -> Self:
        return type(self)(super().__add__(other))

    def __radd__(self, other: Decimal | int, /) -> Self:
        return type(self)(super().__radd__(other))

    def __sub__(self, other: Decimal | int, /) -> Self:
        return type(self)(super().__sub__(other))

    def __truediv__(self, other: Decimal | int, /) -> Self:
        return type(self)(super().__truediv__(other))

    def __pow__(self, other: Decimal | int, mod: Decimal | int | None = None, /) -> Self:
        return type(self)(super().__pow__(other, mod))

    def quantize(self, exp: Decimal | int, rounding: str | None = None, context: Context | None = None) -> Self:
        return type(self)(super().quantize(exp, rounding, context))


class Nominal(Rate):
    """A simple annual rate: a TNA, a fund's annualized day."""


class Annual(Rate):
    """An effective rate, compounded over 365 days or twelve months."""


class Monthly(Rate):
    """An effective rate per month."""


class Daily(Rate):
    """A rate per day."""


class Term(Rate):
    """A rate earned over one quote's own term, not per year."""


# How ARCA pads a comprobante's number, and how this project prints one.
PUNTO_VENTA_DIGITS, NUMERO_DIGITS = 5, 8


def comprobante_label(cbte_tipo: int, punto_venta: int, numero: int) -> str:
    """`21-00005-00000001`: the fiscal identity of one comprobante.

    One definition, because `scaffolding valuation` reconciles the journal against
    the ledger by this string. Two spellings of it would report every pair as an
    orphan and every comprobante as unjournalled.
    """
    return f"{cbte_tipo}-{punto_venta:0{PUNTO_VENTA_DIGITS}d}-{numero:0{NUMERO_DIGITS}d}"


@dataclass(frozen=True)
class Unverified:
    """A figure nothing has confirmed, which must never reach a total as zero.

    Renders as `?` with a pointer to what would settle it, or as `≥ <floor>`
    where part of it is known: a cost made of a fixed component and an unpriced
    one is not the same as a cost nobody has looked at, and printing both as `?`
    threw away the half that was countable.

    Shared, because two things need the same guarantee - `regularization` for a
    legal parameter the index has not confirmed, and the expenditure projection
    for a month with no exchange rate or an obligation whose term was never
    supplied.
    """

    parameter: str
    index_anchor: str
    # What is known to be owed. The unpriced part only ever adds to it, so this
    # is a lower bound and never an estimate.
    floor: Decimal = Decimal(0)


# Every peso figure in a projection. `Unverified` propagates through the
# arithmetic instead of collapsing to zero.
type Money = Decimal | Unverified
