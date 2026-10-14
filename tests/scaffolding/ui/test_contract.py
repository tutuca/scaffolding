"""The contract: a model's fields as the UI asks about them, and the form that follows."""

import types
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest
from django import forms
from django.db import models
from django.forms.widgets import Input

from scaffolding import ui
from scaffolding.data.models import Goal, Movement, Taxpayer
from scaffolding.ui.contract import FORMFIELD_OVERRIDES, Contract, form_class, form_for, formfield_kwargs
from scaffolding.ui.forms import Form as UiForm
from tests.recipes.base import Maker

GOAL_FIELDS = (
    "title",
    "target_date",
    "deadline_date",
    "amount",
    "floor",
    "rank",
    "retires",
    "currency",
    "status",
    "notes",
)

GOOD = {"title": "viaje", "target_date": "2027-01-01", "amount": "100.50", "currency": "USD", "status": "PLANNED"}


def test_the_contract_lists_the_fields_an_instance_has_in_the_order_the_model_declares_them() -> None:
    assert Contract.of(Goal).names == GOAL_FIELDS


def test_the_key_the_timestamps_and_the_owner_are_not_fields_a_person_is_asked_for() -> None:
    names = Contract.of(Goal).names

    assert not {"id", "taxpayer", "created_on", "updated_on"} & set(names)


def test_a_caller_leaves_out_what_its_form_does_not_offer() -> None:
    assert Contract.of(Goal, exclude=["status", "rank", "notes"]).names == (
        "title",
        "target_date",
        "deadline_date",
        "amount",
        "floor",
        "retires",
        "currency",
    )


def test_a_field_says_what_django_knows_about_it() -> None:
    fields = {field.name: field for field in Contract.of(Goal).fields}

    assert (fields["title"].required, fields["title"].max_length, fields["title"].label) == (True, 120, "Meta")
    assert (fields["deadline_date"].required, fields["floor"].required) == (False, False)
    assert ("USD", "Dólar estadounidense") in fields["currency"].choices
    assert fields["floor"].help_text.startswith("Lo mínimo")


def test_the_contract_is_model_agnostic_a_movement_has_its_own_fields() -> None:
    names = Contract.of(Movement).names

    assert {"description", "outflow", "date"} <= set(names) and "taxpayer" not in names


def test_the_contract_module_imports_nothing_of_ours() -> None:
    source = (Path(ui.__file__).parent / "contract.py").read_text()

    assert "from scaffolding" not in source and "import scaffolding" not in source


def test_the_values_of_an_instance_are_the_initial_data_of_its_form(taxpayer: Taxpayer, make_goal: Maker[Goal]) -> None:
    goal = make_goal(title="viaje", amount=Decimal(100), target_date=date(2027, 1, 1))

    values = Contract.of(Goal).values(goal)

    assert (values["title"], values["amount"], values["target_date"], values["deadline_date"]) == (
        "viaje",
        Decimal(100),
        date(2027, 1, 1),
        None,
    )


def test_the_generated_form_has_a_field_per_contract_field_and_validates_like_a_form() -> None:
    form = form_class(Contract.of(Goal))(GOOD)

    assert tuple(form.fields) == GOAL_FIELDS
    assert form.is_valid(), form.errors
    assert form.cleaned_data["amount"] == Decimal("100.50")


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"title": ""}, "title"),
        ({"title": "x" * 121}, "title"),
        ({"amount": "mucho"}, "amount"),
        ({"target_date": "ayer"}, "target_date"),
    ],
)
def test_the_generated_form_refuses_what_the_fields_refuse(change: dict[str, str], field: str) -> None:
    form = form_class(Contract.of(Goal))(GOOD | change)

    assert not form.is_valid()
    assert field in form.errors


def test_the_widgets_say_what_the_browser_can_check() -> None:
    html = str(form_class(Contract.of(Goal))())

    assert 'type="date"' in html
    assert 'maxlength="120"' in html and "required" in html
    assert 'step="0.01"' in html
    assert "<textarea" in html and 'rows="3"' in html


def test_a_date_widget_is_a_date_and_a_datetime_widget_is_not() -> None:
    date_widget = cast(Input, formfield_kwargs(FORMFIELD_OVERRIDES, models.DateField())["widget"])
    datetime_widget = cast(Input, formfield_kwargs(FORMFIELD_OVERRIDES, models.DateTimeField())["widget"])

    assert (date_widget.input_type, datetime_widget.input_type) == ("date", "datetime-local")
    assert formfield_kwargs(FORMFIELD_OVERRIDES, models.CharField()) == {}


def test_the_widget_map_is_replaced_by_passing_another() -> None:
    form = form_class(Contract.of(Goal), overrides={models.DateField: {"widget": forms.TextInput}})()

    assert 'type="date"' not in str(form) and isinstance(form.fields["target_date"].widget, forms.TextInput)


def test_a_form_for_an_instance_starts_with_its_values(taxpayer: Taxpayer, make_goal: Maker[Goal]) -> None:
    goal = make_goal(title="viaje", amount=Decimal(100), target_date=date(2027, 1, 1))

    html = str(form_for(goal, prefix=f"meta{goal.pk}"))

    assert 'value="viaje"' in html and 'value="2027-01-01"' in html and f'name="meta{goal.pk}-title"' in html


def test_a_form_for_a_model_is_empty_and_unbound() -> None:
    form = form_for(Goal)

    assert not form.is_bound and form.initial == {}


def test_data_binds_the_form() -> None:
    form = form_for(Goal, GOOD)

    assert form.is_bound and form.is_valid(), form.errors


def test_a_form_of_that_name_in_the_module_given_is_the_form() -> None:
    class GoalForm(UiForm):
        title = forms.CharField()

    home = types.ModuleType("somewhere")
    home.GoalForm = GoalForm  # type: ignore[attr-defined]

    assert type(form_for(Goal, forms_in=home)) is GoalForm
    assert type(form_for(Goal, forms_in=types.ModuleType("empty"))).__name__ == "GoalForm"
    assert type(form_for(Goal)) is not GoalForm


def test_the_explicit_form_still_gets_the_instances_values(taxpayer: Taxpayer, make_goal: Maker[Goal]) -> None:
    goal = make_goal(title="viaje")

    class GoalForm(UiForm):
        title = forms.CharField()

    home = types.ModuleType("somewhere")
    home.GoalForm = GoalForm  # type: ignore[attr-defined]

    assert form_for(goal, forms_in=home).initial["title"] == "viaje"


def test_a_form_of_ours_is_rendered_by_our_templates_and_one_of_djangos_is_not() -> None:
    ours = str(form_for(Goal))
    theirs = str(type("Plain", (forms.Form,), {"title": forms.CharField()})())

    assert '<ul class="errorlist" data-live hidden aria-live="polite"><li></li></ul>' in ours
    assert "data-live" not in theirs


def test_each_field_of_ours_has_one_slot_for_the_browsers_message() -> None:
    form = form_for(Goal, exclude=["status", "rank", "notes"])

    assert str(form).count("data-live") == len(form.fields)


def test_the_slot_is_beside_the_server_errors_and_before_the_widget() -> None:
    html = str(
        form_for(
            Goal, {"title": "", "amount": "1", "target_date": "2027-01-01", "currency": "USD", "status": "PLANNED"}
        )
    )
    field = html[html.index('<label for="id_title">') : html.index('<label for="id_target_date">')]

    assert field.index("<input") < field.index('class="errorlist"') < field.index("data-live")


def test_a_summary_is_every_error_in_one_list_each_field_under_its_label() -> None:
    form = form_for(
        Goal, {"title": "", "amount": "mucho", "target_date": "2027-01-01", "currency": "USD", "status": "PLANNED"}
    )
    form.add_error(None, "no entra en el plan")

    html = str(form.summary)

    assert html.count("<li>") == 3 and '<ul class="errorlist nonfield">' not in html
    assert "no entra en el plan" in html and "Meta: " in html and "Importe: " in html


def test_a_summary_with_nothing_wrong_is_nothing() -> None:
    assert str(form_for(Goal, GOOD).summary) == ""
    assert str(form_for(Goal).summary) == ""


def test_a_caller_names_the_fields_and_their_order_as_a_model_form_does() -> None:
    contract = Contract.of(Goal, fields=["amount", "title", "currency"])

    assert contract.names == ("amount", "title", "currency")
    assert tuple(form_class(contract)().fields) == ("amount", "title", "currency")


def test_a_field_the_model_does_not_offer_is_not_one_a_caller_can_name() -> None:
    with pytest.raises(KeyError):
        Contract.of(Goal, fields=["title", "id"])


def test_the_values_a_caller_gives_win_over_the_instances(taxpayer: Taxpayer, make_goal: Maker[Goal]) -> None:
    goal = make_goal(title="viaje")

    form = form_for(goal, initial={"title": "otro"})

    assert form.initial["title"] == "otro" and form.initial["amount"] == goal.amount
