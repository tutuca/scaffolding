"""The vocabulary every layer shares."""

from decimal import Decimal

from scaffolding.types import Annual, Monthly, Unverified, comprobante_label


def test_comprobante_label_pads_the_punto_de_venta_and_the_numero():
    assert comprobante_label(21, 5, 1) == "21-00005-00000001"


def test_unverified_carries_the_parameter_and_a_floor():
    """A cost part known and part unpriced is not a cost nobody has looked at."""
    unknown = Unverified(parameter="loan term", index_anchor="obligation.ends_on")

    assert unknown.floor == Decimal(0)
    assert Unverified(parameter="p", index_anchor="a", floor=Decimal(5)).floor == Decimal(5)


def test_rate_arithmetic_keeps_the_period():
    """Adding, compounding and rounding a rate does not shed its period.

    The period is the type's whole job: `Annual + Annual` is still an `Annual`,
    and Fisher's deflation reads as the math it is without an outer constructor.
    """
    nominal, inflation = Annual("0.23"), Annual("0.30")
    real = (1 + nominal) / (1 + inflation) - 1

    assert type(real) is Annual
    assert real.quantize(Decimal("0.000001")) == Decimal("-0.053846")
    assert type((1 + Monthly("0.02")) ** 12 - 1) is Monthly


def test_money_times_a_rate_is_money_not_a_rate():
    """`amount * monthly_rate` is a balance, not a rate, and the type says so."""
    monthly = Monthly("0.02")

    assert type(Decimal(1000) * monthly) is Decimal
