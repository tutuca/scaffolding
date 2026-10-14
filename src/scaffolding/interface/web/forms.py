"""The web shell's forms, over the base renderer in `ui/forms.py`."""

from django.contrib.auth.forms import AuthenticationForm

from scaffolding.ui.forms import Form


class LoginForm(Form, AuthenticationForm):
    """Django's login form, wearing the project's form markup.

    `Form` is first in the MRO, so its `default_renderer` wins and the fields
    render through `ui/components/form/` rather than Django's default `div.html`.
    """
