"""Deploy-time checks: what a machine facing the network must fix first.

`scaffolding check` skips these; `scaffolding check --deploy` lists them, and a
release is only cut when that list is clean (docs/INFRASTRUCTURE.md). The
SECRET_KEY check is the listing half of `conf/serving.py`'s refusal, which
enforces the same rule at serve time.
"""

from collections.abc import Sequence

from django.apps.config import AppConfig
from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.security, deploy=True)
def insecure_secret_key_is_refused(*, app_configs: Sequence[AppConfig] | None = None, **kwargs: object) -> list[Error]:
    """The default SECRET_KEY: sessions are forgeable until a real one is set."""
    if not settings.DEBUG and settings.SECRET_KEY == settings.INSECURE_SECRET_KEY:
        return [
            Error(
                "the default SECRET_KEY is in use",
                hint="set SECRET_KEY in .env (see .env.example); sessions are forgeable until it is",
                id="scaffolding.security.W001",
            )
        ]
    return []
