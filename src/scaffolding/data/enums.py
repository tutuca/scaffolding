from django.db import models


class Currency(models.TextChoices):
    USD = "USD", "Dólar estadounidense"
    ARS = "ARS", "Peso argentino"


class RateSource(models.TextChoices):
    ARCA = "ARCA", "ARCA (cotización registrada)"
    MEP = "MEP", "Dólar MEP (bolsa)"
    CCL = "CCL", "Dólar contado con liquidación"
    MANUAL = "MANUAL", "Carga manual"


class Indicator(models.TextChoices):
    """One published market index, national and daily.

    The slugs are this project's and the labels the publisher's own. A rate
    reading is a percentage (`23.75` is 23,75%); `market.calc` turns it into a
    fraction and derives the TEA and the TEM. A spread - `embi` - is a level in
    points, not a compounding rate, so `market.calc` does not restate it
    (`SPREAD_INDICATORS` below). `tasa-politica-monetaria` went flat when policy
    moved to pases and TAMAR, so it is kept beside the two rates the market
    actually clears at.
    """

    TASA_POLITICA_MONETARIA = "tasa-politica-monetaria", "Tasa de política monetaria"
    TAMAR = "tamar", "TAMAR bancos privados"
    BADLAR = "badlar", "BADLAR bancos privados"
    EMBI = "embi", "Riesgo país (EMBI+)"


class MarketSource(models.TextChoices):
    """Who published a `MarketIndex` reading.

    The free mirrors are named individually - not a generic "mirror" - so a
    consensus can say which sources it pooled and how far they disagree.
    """

    BCRA = "BCRA", "BCRA (API)"
    MANUAL = "MANUAL", "Carga manual"
    AMBITO = "AMBITO", "Ámbito"
    CRONISTA = "CRONISTA", "El Cronista"


# Which indicators are a spread printed in points rather than a rate restated as
# TEA/TEM. A table, searched: adding a spread is a row, and `market report` reads
# it rather than guessing a conversion.
SPREAD_INDICATORS = frozenset({Indicator.EMBI})


class Division(models.TextChoices):
    """One series of INDEC's consumer price index: national, monthly.

    Twelve COICOP divisions, plus `nivel-general` (the whole basket) and the three
    special aggregates `nucleo`, `regulados` and `estacionales` - INDEC's own
    decomposition of the index into its inertial/conflict, policy/tariff and
    supply components (`docs/INFLATION.md`). The slugs are this project's and the
    labels are INDEC's own. None of the four is a COICOP division, and all are
    stored beside the twelve anyway, because each is the same kind of monthly
    index and one table with one shape gives one report.
    """

    NIVEL_GENERAL = "nivel-general", "Nivel general"
    NUCLEO = "nucleo", "Núcleo"
    REGULADOS = "regulados", "Regulados"
    ESTACIONALES = "estacionales", "Estacionales"
    ALIMENTOS_BEBIDAS = "alimentos-bebidas", "Alimentos y bebidas no alcohólicas"
    BEBIDAS_TABACO = "bebidas-tabaco", "Bebidas alcohólicas y tabaco"
    PRENDAS_CALZADO = "prendas-calzado", "Prendas de vestir y calzado"
    VIVIENDA_SERVICIOS = "vivienda-servicios", "Vivienda, agua, electricidad y otros combustibles"
    EQUIPAMIENTO_HOGAR = "equipamiento-hogar", "Equipamiento y mantenimiento del hogar"
    SALUD = "salud", "Salud"
    TRANSPORTE = "transporte", "Transporte"
    COMUNICACIONES = "comunicaciones", "Comunicaciones"
    RECREACION_CULTURA = "recreacion-cultura", "Recreación y cultura"
    EDUCACION = "educacion", "Educación"
    RESTAURANTES_HOTELES = "restaurantes-hoteles", "Restaurantes y hoteles"
    BIENES_SERVICIOS_VARIOS = "bienes-servicios-varios", "Bienes y servicios varios"


class LaborSeries(models.TextChoices):
    """One series of INDEC's wage and living-cost tables: national, monthly.

    Two kinds share one shape - a level at a date. The `salarios` series are an
    index (octubre 2016 = 100), the price of labour power; the `canasta` series
    are pesos corrientes, the cost of reproducing labour power (the CBA/CBT for
    the adulto equivalente). The slugs are this project's and the labels INDEC's
    own. They are stored beside each other in one table because `scaffolding
    inflation report` reads the wage against the canasta, and one table with one
    shape gives one report - the same reason the IPC divisions and their special
    aggregates share `PriceIndex` (`docs/INFLATION.md`).
    """

    SALARIOS = "salarios", "Salarios (general)"
    SALARIOS_REGISTRADO = "salarios-registrado", "Salarios registrados"
    SALARIOS_PRIVADO = "salarios-privado", "Salarios registrados, sector privado"
    SALARIOS_PUBLICO = "salarios-publico", "Salarios registrados, sector público"
    SALARIOS_NO_REGISTRADO = "salarios-no-registrado", "Salarios no registrados"
    CBA = "cba", "Canasta básica alimentaria"
    CBT = "cbt", "Canasta básica total"


class InvoiceStatus(models.TextChoices):
    DRAFT = "DRAFT", "Borrador"
    AUTHORIZED = "AUTHORIZED", "Autorizada (CAE)"
    REJECTED = "REJECTED", "Rechazada por ARCA"
    VOID = "VOID", "Anulada"


class CbteTipo(models.IntegerChoices):
    """ARCA comprobante codes for export documents."""

    FACTURA_E = 19, "Factura E"
    NOTA_DEBITO_E = 20, "Nota de Débito E"
    NOTA_CREDITO_E = 21, "Nota de Crédito E"


class BillingCadence(models.TextChoices):
    MONTHLY = "MONTHLY", "Mensual"


class Institution(models.TextChoices):
    GALICIA = "GALICIA", "Banco Galicia"
    PAYONEER = "PAYONEER", "Payoneer"
    NACION = "NACION", "Banco Nación"
    AMEX = "AMEX", "American Express"
    # A home whose bank no parser names yet. The plan's kind still says what the
    # product is; this is only "not one of the four above".
    OTROS = "OTROS", "Otros"


# The institutions whose statement is a card's, not an account's: a credit on
# one is the card being paid, never money coming in. A table, searched by the
# reads that total income; a second card is a row here.
CARDS = frozenset({Institution.AMEX})


class MovementKind(models.TextChoices):
    """What a movement does to the balance, once something has classified it.

    Stored rather than derived: a Payoneer balance conversion is an inflow that is
    not income, so "has an inflow" cannot stand in for "is a client payment". Blank
    until classified - the importer sets it for the rails it understands, and a
    person sets it in the admin for a wire no parser produces.
    """

    CREDIT = "CREDIT", "Cobro de un cliente"
    DEBIT = "DEBIT", "Pago a un tercero"
    WITHDRAWAL = "WITHDRAWAL", "Retiro a una cuenta propia"
    REVERSAL = "REVERSAL", "Cobro revertido"
    NO_MOVEMENT = "NO_MOVEMENT", "Sin movimiento (0,00)"
    UNKNOWN = "UNKNOWN", "Sin reconocer"


class TipoExpo(models.IntegerChoices):
    """ARCA's export categories (FEXGetPARAM_Tipo_Expo, read 2026-09-09)."""

    BIENES = 1, "Exportación definitiva de bienes"
    SERVICIOS = 2, "Servicios"
    OTROS = 4, "Otros"


class IdiomaCbte(models.IntegerChoices):
    """Language the comprobante is printed in (FEXGetPARAM_Idiomas)."""

    ESPANOL = 1, "Español"
    INGLES = 2, "Inglés"
    PORTUGUES = 3, "Portugués"


class UnidadMedida(models.IntegerChoices):
    """Only the units this project bills in (FEXGetPARAM_UMed lists about thirty)."""

    UNIDADES = 7, "unidades"


# WSFEX names currencies in its own three-letter table, not ISO 4217: the US
# dollar is "DOL", not "USD" (FEXGetPARAM_MON).
ARCA_CURRENCY: dict[str, str] = {Currency.USD: "DOL", Currency.ARS: "PES"}


class OnMaturity(models.TextChoices):
    """What the bank's standing instruction does with a deposit when it matures."""

    RENEW_ALL = "RENEW_ALL", "Renueva capital e interés"
    RENEW_PRINCIPAL = "RENEW_PRINCIPAL", "Renueva el capital, acredita el interés"
    WITHDRAW = "WITHDRAW", "No renueva: acredita todo"


class GoalStatus(models.TextChoices):
    PLANNED = "PLANNED", "Pendiente"
    DONE = "DONE", "Cumplido"
    DROPPED = "DROPPED", "Descartado"


class BalanceSource(models.TextChoices):
    """Where a recorded balance came from.

    `LEDGER` is the running balance the statement already printed on its last
    row, which two of the four institutions report and two do not. `MANUAL` is
    the closing line read by a person, which is the only way to get the others.
    """

    LEDGER = "LEDGER", "Saldo del extracto"
    MANUAL = "MANUAL", "Carga manual"


class Bucket(models.TextChoices):
    """The coarse cut, read first: is this spending, and could it give?

    `needs` and `wants` are Warren & Tyagi's two spending legs; `structural` is
    the third thing their split has no name for - money moving, debt service, tax
    and losses - which the projection's baseline refuses to count as spending.
    That distinction used to live in a second list beside the rules; it lives
    here, once.

    `income` is the fourth, and the only one that is not spending at all. It is
    here because a credit still needs a categoría - left blank it reads as
    `sin decidir`, and a year of client payments sitting in the triage queue is a
    question nobody has to answer. Calling it `structural` instead would have the
    ledger assert that money arriving is a kind of expense.

    English, like every other identifier here: the project reserves Spanish for
    ARCA's own field names, and a bucket is not one of them.
    """

    NEEDS = "needs", "Necesidades"
    WANTS = "wants", "Gustos"
    STRUCTURAL = "structural", "Estructural (no es gasto)"
    INCOME = "income", "Ingreso (entra, no sale)"


class Role(models.TextChoices):
    """What a profile may do on one taxpayer's books.

    The line between OWNER and ACCOUNTANT is managing the credentials versus
    using them: a contador authorizing an invoice uses the certificate, which is
    not the same as being able to replace it.
    """

    OWNER = "OWNER", "Titular"
    ACCOUNTANT = "ACCOUNTANT", "Contador"
    VIEWER = "VIEWER", "Lectura"


class RuleDirection(models.TextChoices):
    """Which side of a statement a categorization rule reads: what left, or what arrived."""

    DEBIT = "debit", "Débito"
    CREDIT = "credit", "Crédito"


class PriceBasis(models.TextChoices):
    """The unit a categoría's payments can be read as a price in, when they can: a plan's fee,
    a litre, a kilowatt-hour, a cubic metre."""

    FEE = "cuota", "Cuota"
    LITRE = "litro", "Litro"
    KWH = "kWh", "kWh"
    CUBIC_METRE = "m³", "m³"
