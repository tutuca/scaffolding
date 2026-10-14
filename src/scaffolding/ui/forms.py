"""The base of every form we render: Django's own, with templates that are ours.

Django renders a form from two templates, one for the form and one for each field, and the
renderer says which (`form_template_name`, `field_template_name`). A renderer of our own
gives every form the known markup the page's stylesheet and scripts are written against -
the same `{{ form }}` a template already writes, with the slots a script can fill - and
leaves every other form alone, the admin's included: it is set on this base class, not on
`FORM_RENDERER`.
"""

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms.renderers import DjangoTemplates
from django.forms.utils import ErrorList


class Renderer(DjangoTemplates):
    form_template_name = "ui/components/form/form.html"
    field_template_name = "ui/components/form/form_field.html"


class Form(forms.Form):
    default_renderer = Renderer()

    @property
    def summary(self) -> ErrorList:
        """Every error of the form in one list - the form's own first, then each field's under
        its label - for a form whose fields are laid out where an error cannot sit beside
        them, the cells of a table. Django's own `ErrorList` draws it, so it is the markup
        every other error already is: `{{ form.summary }}`, and nothing when there are none.
        (`form.errors` would draw the same list under the fields' names, `rank_3`, not what
        the reader was shown.)"""
        lines = [str(error) for error in self.non_field_errors()]
        lines += [
            f"{self[name].label}: {error}"
            for name, errors in self.errors.items()
            if name != NON_FIELD_ERRORS
            for error in errors
        ]
        return self.error_class(lines, renderer=self.renderer)
