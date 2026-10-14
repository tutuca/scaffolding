"""The API's schema and our own contract describe the same fields the same way.

Two readers of one model - `_meta`, for the forms (`ui/contract.py`), and the serializers, for the
API and the schema it serves - must not drift. Where they differ on purpose it is said here.
"""

from datetime import date
from decimal import Decimal
from typing import cast

import pytest
from django.template import Context, Template

from scaffolding.data.models import Goal
from scaffolding.ui.contract import Contract
from scaffolding.ui.schema import components, kind_of, properties, schema_of

pytestmark = pytest.mark.django_db


def spec_of(name: str) -> dict[str, object]:
    return properties(schema_of(Goal))[name]


@pytest.mark.parametrize("field", Contract.of(Goal).fields, ids=lambda field: field.name)
def test_a_field_is_the_same_field_to_the_form_and_to_the_schema(field) -> None:  # type: ignore[no-untyped-def]
    prop = spec_of(field.name)

    assert prop["title"] == field.label
    assert prop.get("description", "") == field.help_text
    assert bool(prop.get("nullable")) == field.column.null
    if not field.choices:
        # A choice is bounded by its list: the schema says `enum`, not a length.
        assert prop.get("maxLength") == field.max_length


def test_what_the_schema_requires_the_form_requires() -> None:
    """The reverse is not true on purpose: a field with a default (the currency, the status) is
    not required of an API request, but a form asks for its value, since a select always has one."""
    required = set(schema_of(Goal)["required"])  # type: ignore[call-overload]
    writable = {name for name, prop in properties(schema_of(Goal)).items() if not prop.get("readOnly")}

    for field in Contract.of(Goal).fields:
        assert field.name not in required & writable or field.required


def test_the_values_of_a_choice_are_the_values_the_schema_lists() -> None:
    for name in ("currency", "status"):
        field = next(one for one in Contract.of(Goal).fields if one.name == name)
        ref = spec_of(name)["allOf"][0]["$ref"]  # type: ignore[index]
        values = cast(list[str], components()[ref.rsplit("/", 1)[1]]["enum"])

        assert values == [value for value, _ in field.choices]


@pytest.mark.parametrize(
    ("name", "kind"),
    [
        ("amount", "number"),
        ("floor", "number"),
        ("rank", "number"),
        ("target_date", "date"),
        ("title", "text"),
        ("currency", "text"),
    ],
)
def test_a_field_is_a_column_of_one_of_three_kinds(name: str, kind: str) -> None:
    assert kind_of(spec_of(name)) == kind


def test_what_a_person_cannot_write_is_read_only_in_the_schema_and_not_in_the_contract() -> None:
    props = properties(schema_of(Goal))

    assert props["id"]["readOnly"] and props["created_on"]["readOnly"] and props["updated_on"]["readOnly"]
    assert not {"id", "created_on", "updated_on"} & set(Contract.of(Goal).names)
    # The API narrows further than the model does: the status, the rank and the notes are written
    # by the entry points (complete, drop, restore, order), so over HTTP they are read only,
    # while the contract - what the model has - still lists them and a form picks its own fields.
    assert all(props[name]["readOnly"] for name in ("status", "rank", "notes"))
    assert "taxpayer" not in props


def test_a_model_with_no_endpoint_has_no_component() -> None:
    class Unexposed:
        __name__ = "Unexposed"

    with pytest.raises(KeyError):
        schema_of(Unexposed)  # type: ignore[arg-type]


def test_the_head_tag_writes_a_columns_head_from_the_field() -> None:
    html = Template('{% load grid %}{% head schema "floor" %}{% head schema "title" %}').render(
        Context({"schema": schema_of(Goal)})
    )

    assert html == (
        '<th scope="col" data-key="floor" data-sort="number" class="num">Mínimo</th>'
        '<th scope="col" data-key="title" data-sort="text">Meta</th>'
    )


def render(source: str, **context: object) -> str:
    return Template("{% load grid %}" + source).render(Context({"schema": schema_of(Goal)} | context))


def test_the_cell_tag_owns_what_the_kind_decides_and_the_page_what_is_shown() -> None:
    html = render(
        '{% cell schema "amount" amount %}USD {{ money }}{% endcell %}'
        '{% cell schema "target_date" when %}{{ when|date:"Y-m" }}{% endcell %}'
        '{% cell schema "title" "viaje" %}viaje{% endcell %}',
        amount=Decimal("1500.00"),
        money="1.500",
        when=date(2027, 3, 1),
    )

    assert html == (
        '<td class="num" data-value="1500.00">USD 1.500</td><td data-value="2027-03-01">2027-03</td><td>viaje</td>'
    )


def test_a_cell_with_no_value_carries_no_raw_value_to_sort_by() -> None:
    assert render('{% cell schema "floor" nothing %}—{% endcell %}', nothing=None) == '<td class="num">—</td>'


def test_what_is_shown_is_escaped_as_anywhere_in_a_template() -> None:
    assert render('{% cell schema "title" t %}{{ t }}{% endcell %}', t="<b>") == "<td>&lt;b&gt;</td>"
