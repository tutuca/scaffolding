"""The forms the pages ask for: a goal's (generated from the model's contract,
not written out), the movimientos search, the goals' order, the naming of
unnamed movements, the taxpayer registration and the ARCA certificate's files."""

from collections.abc import Mapping, Sequence

from django import forms
from django.http import QueryDict

from scaffolding.data.models import Goal
from scaffolding.service.domain.expenses.schemas import Pending
from scaffolding.ui.contract import form_for
from scaffolding.ui.forms import Form


class RegisterTaxpayerForm(Form):
    """The punto de venta is offered because ARCA assigns it separately and a
    new monotributista may not have one yet."""

    tax_id = forms.CharField(label="CUIT", max_length=13, help_text="con o sin guiones")
    punto_venta = forms.IntegerField(label="Punto de venta", required=False, min_value=1)


# What a goal's form asks for, in the order it asks: not a form written out, but the model's own
# field contract (`ui/contract.py`) - labels, hints, sizes and kinds are on `Goal` - narrowed
# to what a person says and not what the plan keeps (the order, the status, the notes).
GOAL_FIELDS = ("title", "amount", "currency", "target_date", "deadline_date", "floor", "retires")


def goal_prefix(goal: int | None) -> str:
    """Every goal has its own form on the page, so each names its fields apart:
    `nueva` is the empty one."""
    return "nueva" if goal is None else f"meta{goal}"


def goal_form(
    data: Mapping[str, object] | None = None, *, goal: int | None = None, initial: Mapping[str, object] | None = None
) -> Form:
    """The form for a goal - the new one, or goal `goal` with its values as `initial`."""
    return form_for(Goal, data, prefix=goal_prefix(goal), fields=GOAL_FIELDS, initial=initial)


class SearchForm(Form):
    """The search of a list that is paged and ordered: the words, and the order and page-less
    state a search keeps (they ride along as hidden fields, so searching does not forget how
    the list was ordered)."""

    q = forms.CharField(
        label="Buscar",
        required=False,
        help_text="Escribir filtra esta página; Enter busca en todos los que faltan nombrar.",
        widget=forms.TextInput(attrs={"type": "search", "autocomplete": "off", "data-filter": True}),
    )
    s = forms.CharField(required=False, widget=forms.HiddenInput)
    d = forms.CharField(required=False, widget=forms.HiddenInput)


class PlacementForm(Form):
    """What the placement schedule is asked: how many months of spending stay liquid, and what is
    cut from the baseline to see what that would free. Sent by GET, so the answer has an address."""

    colchon = forms.DecimalField(
        label="Colchón, en meses de gasto",
        min_value=0,
        max_value=12,
        decimal_places=1,
        required=False,
        help_text="Lo que queda líquido antes de colocar. La referencia es de 3 a 6 meses (docs/BUDGET.md).",
    )
    recorte = forms.CharField(
        label="Recortes",
        required=False,
        help_text="categoría=pesos por mes o categoría=%, separados por coma: mercadopago-big=500000, pedidos ya=30%",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )


class OrderForm(Form):
    """The place of each pending goal in the order they are paid: a number per goal,
    empty to leave it to the plan. One field per goal, so a bad number is named by the
    goal it is on."""

    def __init__(self, data: QueryDict | None = None, *, ranks: Mapping[int, int | None]) -> None:
        super().__init__(data)
        for goal, rank in ranks.items():
            self.fields[f"rank_{goal}"] = forms.IntegerField(
                label=f"Orden de la meta {goal}",
                required=False,
                min_value=1,
                initial=rank,
                widget=forms.NumberInput(attrs={"form": "orden"}),
            )

    def ranks(self) -> dict[int, int | None]:
        return {int(name.removeprefix("rank_")): value for name, value in self.cleaned_data.items()}


class NamingForm(Form):
    """A categoría for some of the unnamed movements, each chosen from the taxonomy.

    One field per movement on the page, named by its reference, so a number is
    never read against a row that has since moved. Empty leaves it unnamed; a
    form with nothing chosen is refused, because it would be a button that does
    nothing."""

    def __init__(
        self, data: QueryDict | None = None, *, pending: Sequence[Pending], vocabulary: Mapping[str, Sequence[str]]
    ) -> None:
        super().__init__(data, label_suffix="")
        choices = [("", "—"), *((heading, [(name, name) for name in names]) for heading, names in vocabulary.items())]
        for row in pending:
            self.fields[f"name_{row.reference}"] = forms.ChoiceField(
                label=f"Categoría de {row.description}",
                choices=choices,
                required=False,
                widget=forms.Select(attrs={"form": "nombrar"}),
            )
            if row.similar:
                self.fields[f"alike_{row.reference}"] = forms.BooleanField(
                    label=f"y los {row.similar} de «{row.payee}»",
                    required=False,
                    widget=forms.CheckboxInput(attrs={"form": "nombrar"}),
                )

    def clean(self) -> dict[str, str]:
        cleaned = super().clean() or {}
        if not any(value for name, value in cleaned.items() if name.startswith("name_")):
            raise forms.ValidationError("Elegí una categoría para al menos un movimiento.")
        return cleaned

    def namings(self) -> dict[str, str | None]:
        return {
            name.removeprefix("name_"): value
            for name, value in self.cleaned_data.items()
            if name.startswith("name_") and value
        }

    def alike(self) -> list[str]:
        """The movements whose categoría is to be spread to everyone who paid the same."""
        return [
            name.removeprefix("alike_")
            for name, value in self.cleaned_data.items()
            if name.startswith("alike_") and value
        ]


class CertificateForm(Form):
    """The two files ARCA's flow produces: the certificate it issued and the
    key that never left this machine."""

    certificate = forms.FileField(label="Certificado (arca.pem)")
    key = forms.FileField(label="Clave privada (arca.key)")
