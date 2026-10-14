"""The one refusal before `runserver` starts serving.

A fresh install has a working default SECRET_KEY so the suite and a local
shell run without configuration - and that same default would let anyone
forge sessions if the machine answered the network. `manage.py` calls
`refuse_insecure_key` before Django boots the server; `data/checks.py` lists
the same rule for `scaffolding check --deploy`. Two askers, one answer: the
operator who serves and the checklist that audits.
"""

from django.conf import settings
from django.core.management.base import CommandError


def refuse_insecure_key() -> None:
    """Raise unless serving with a real SECRET_KEY, or locally with DEBUG on."""
    if not settings.DEBUG and settings.SECRET_KEY == settings.INSECURE_SECRET_KEY:
        raise CommandError(
            "refusing to serve with the default SECRET_KEY - sessions would be forgeable. "
            "Set SECRET_KEY in .env (see .env.example), or run with DEBUG=true for local development."
        )
