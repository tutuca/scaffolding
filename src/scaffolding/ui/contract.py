"""The contract: what a model says to the UI, and the form that follows from it.

A model is a contract here and nothing more: it lists the fields an instance has, and
Django already knows everything about each - its kind, its size, whether it may be blank,
its choices. `Contract.of(model)` reads that list off `_meta` and hands it over as plain
values; it imports no model of ours, so the same call serves a goal and a movement.
Querysets and managers are for later.

Validation logic is not here. The contract describes fields; what makes a goal valid is a
form's and the domain's, found by convention: a form class named `<Model>Form` in the
module the caller points at wins (`form_for(..., forms_in=...)`), and when there is none the
form is generated from the contract - Django's own `Field.formfield()` for each field, with
a table of replacements for what the browser should be given (`FORMFIELD_OVERRIDES`, the
shape of the admin's `formfield_overrides`: a model field class, and the keyword arguments
its form field is made with). A plain `forms.Form`, not a `ModelForm`: a `ModelForm` assigns
onto the instance while it validates, and model fields are assigned by the model's
mutators and by nothing else.
"""

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from types import ModuleType

from django import forms
from django.db import models
from django.utils.text import capfirst

from .forms import Form

# Every owned model has a tenant, and no form ever asks for it: the shell says whose.
OWNER = "tenant"

type Column = models.Field[object, object]

# A model field class -> the keywords its form field is made with. The first class in the
# field's own MRO that has an entry is used, so a subclass is its own entry or its parent's.
FORMFIELD_OVERRIDES: dict[type[Column], dict[str, object]] = {
    models.DateField: {"widget": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")},
    models.DateTimeField: {"widget": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")},
    models.TextField: {"widget": forms.Textarea(attrs={"rows": 3})},
}


@dataclass(frozen=True)
class Field:
    """One field of an instance, as the UI asks about it. The model field is kept whole:
    it is the one place a kind, a size and a choice list are written down."""

    column: Column

    @property
    def name(self) -> str:
        return self.column.name

    @property
    def label(self) -> str:
        return capfirst(str(self.column.verbose_name))

    @property
    def required(self) -> bool:
        return not self.column.blank

    @property
    def help_text(self) -> str:
        return str(self.column.help_text)

    @property
    def max_length(self) -> int | None:
        return self.column.max_length

    @property
    def choices(self) -> tuple[tuple[object, str], ...]:
        return tuple((value, str(label)) for value, label in self.column.flatchoices)


@dataclass(frozen=True)
class Contract:
    model: type[models.Model]
    fields: tuple[Field, ...]

    @classmethod
    def of(
        cls, model: type[models.Model], *, fields: Sequence[str] | None = None, exclude: Collection[str] = ()
    ) -> Contract:
        """The fields a person could be asked for: the editable ones, in the order the model
        declares them, without the key, the owner and whatever `exclude` names - or, as a
        `ModelForm`'s `fields` does, exactly these and in this order."""
        skipped = {OWNER, *exclude}
        columns = [
            column
            for column in model._meta.concrete_fields
            if column.editable and not column.primary_key and column.name not in skipped
        ]
        if fields is not None:
            wanted = {column.name: column for column in columns}
            columns = [wanted[name] for name in fields]
        return cls(model, tuple(Field(column) for column in columns))

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(field.name for field in self.fields)

    def values(self, instance: models.Model) -> dict[str, object]:
        """What an instance holds for each of these fields: the initial data of its form."""
        return {field.name: field.column.value_from_object(instance) for field in self.fields}


def formfield_kwargs(table: Mapping[type[Column], dict[str, object]], column: Column) -> dict[str, object]:
    for kind in type(column).__mro__:
        if kind in table:
            return dict(table[kind])
    return {}


def form_class(contract: Contract, *, overrides: Mapping[type[Column], dict[str, object]] | None = None) -> type[Form]:
    """A form for the contract: each field Django's own form field for the model field,
    made with the overrides - ours, then the caller's."""
    table = FORMFIELD_OVERRIDES | dict(overrides or {})
    made = {
        field.name: field.column.formfield(**formfield_kwargs(table, field.column))  # type: ignore[arg-type]
        for field in contract.fields
    }
    return type(f"{contract.model.__name__}Form", (Form,), {name: made[name] for name in made})


def form_for(
    subject: models.Model | type[models.Model],
    data: Mapping[str, object] | None = None,
    *,
    forms_in: ModuleType | None = None,
    prefix: str | None = None,
    fields: Sequence[str] | None = None,
    exclude: Collection[str] = (),
    initial: Mapping[str, object] | None = None,
    overrides: Mapping[type[Column], dict[str, object]] | None = None,
) -> Form:
    """The form for an instance (its values are the initial data) or for a model (empty).

    A `<Model>Form` in `forms_in` is the form, if there is one; otherwise it is generated
    from the contract. Either way it is a plain form of ours (`ui.forms.Form`: the explicit one
    is written to extend it), bound when there is `data`."""
    instance = subject if isinstance(subject, models.Model) else None
    model = type(subject) if isinstance(subject, models.Model) else subject
    contract = Contract.of(model, fields=fields, exclude=exclude)
    explicit = getattr(forms_in, f"{model.__name__}Form", None) if forms_in is not None else None
    cls = explicit or form_class(contract, overrides=overrides)
    values = contract.values(instance) if instance is not None else {}
    return cls(data, initial=values | dict(initial or {}) or None, prefix=prefix)
