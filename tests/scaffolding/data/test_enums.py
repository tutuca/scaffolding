"""The codes ARCA publishes, transcribed rather than trusted.

A wrong code here is a rejected comprobante, so the values are asserted the way
`test_mapping_requests.py` asserts the element order: read off ARCA's own
reference tables, on the date named, and pinned.
"""

from scaffolding.data.enums import ARCA_CURRENCY, Currency, IdiomaCbte, TipoExpo, UnidadMedida


def test_the_export_codes_are_the_ones_arca_publishes() -> None:
    """From FEXGetPARAM_Tipo_Expo / _Idiomas / _UMed / _MON on 2026-09-09."""
    assert TipoExpo.SERVICIOS.value == 2
    assert IdiomaCbte.INGLES.value == 2
    assert UnidadMedida.UNIDADES.value == 7


def test_wsfex_names_the_dollar_in_its_own_table_not_iso_4217() -> None:
    """`DOL`, not `USD`. Sending the ISO code is a rejected comprobante."""
    assert ARCA_CURRENCY[Currency.USD] == "DOL"
    assert ARCA_CURRENCY[Currency.ARS] == "PES"
