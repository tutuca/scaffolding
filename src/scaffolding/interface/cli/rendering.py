"""How the CLI prints: the constancia, and the expense chart.

Rendering only - every function here takes a read model and returns text. It
holds no rules, so nothing in it needs the ORM.

The constancia renderers live here rather than in `service/domain/tax/` because
the probe (`bin/arca_padron.py`) imports them without Django's app registry, and
importing the tax package runs its `__init__`, which pulls the ORM. The command
and the probe share one definition, so they cannot drift on what a field is
called.
"""

import dataclasses
import json
from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from scaffolding.interface.adapter.arca.ports import TaxpayerRegistration


def plain(registration: TaxpayerRegistration) -> str:
    """The read model for a person, one field a line."""
    rows = (
        ("cuit", registration.cuit),
        ("razón social", registration.razon_social),
        ("régimen", registration.regimen),
        ("situación IVA", registration.situacion_iva),
        ("categoría", registration.monotributo_categoria),
        ("actividad", registration.actividad),
        ("estado CUIT", registration.estado_cuit),
        ("domicilio", registration.domicilio_fiscal),
        ("impuestos", ", ".join(registration.impuestos)),
        ("leído", registration.fetched_on),
    )
    lines = [f"{label:<14} {value or '-'}" for label, value in rows]
    if registration.errors:
        lines.append(f"{'avisos':<14} {'; '.join(registration.errors)}")
    return "\n".join(lines)


def json_value(value: object) -> object:
    """Dataclasses, exact amounts and ISO dates are the CLI's interchange shapes."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(value)
    if isinstance(value, (Decimal, date)):
        return str(value)
    raise TypeError(f"Cannot serialize {type(value).__name__}.")


def as_json(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, default=json_value)


def bars(rows: Sequence[tuple[str, Decimal]], width: int = 60) -> list[str]:
    """A plain-text bar chart: label, amount, and a bar scaled to the largest row.

    Text so it lands in a terminal, a chat or a log, the way
    `bin/extractos_report.py` did before the movements table replaced its store.
    An empty report renders as a sentence rather than as nothing, so the reader
    can tell "no gastos" from "the command did not run".
    """
    if not rows:
        return ["(sin egresos)"]
    labels = max(len(label) for label, _ in rows)
    largest = max(amount for _, amount in rows)
    bar = width - labels - 16
    return [
        f"  {label:<{labels}} {amount:>14,.0f}  {'█' * (round(amount / largest * bar) if largest else 0)}"
        for label, amount in rows
    ]
