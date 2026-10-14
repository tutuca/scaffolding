"""Forms are Django's own div layout, dressed by the page's form stylesheet
(`components/form/form.css`).

The admin loads `tokens.css` and `chrome.css` and brings its own form styling, so
the page stylesheet reaching it would restyle every changeform. Scope is part of
the claim: this reads the admin's base template, not a rendered admin page.
"""

from pathlib import Path

from scaffolding.interface.web.forms import goal_form

TEMPLATES = Path(__file__).parents[3] / "src/scaffolding/ui/templates"


def test_the_admin_never_loads_the_page_stylesheet() -> None:
    assert "page.css" not in (TEMPLATES / "admin/base.html").read_text()


def test_a_field_that_erred_is_marked_for_the_stylesheet_and_the_screen_reader() -> None:
    form = goal_form(
        {"nueva-title": "", "nueva-amount": "1", "nueva-currency": "USD", "nueva-target_date": "2027-01-01"}
    )

    html = str(form)

    assert 'aria-invalid="true"' in html
    assert "<div>" in html or "<div" in html
