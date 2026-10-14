"""URL reversing for the versioned API.

Routes are served under `/api/v<version>/` via DRF's `URLPathVersioning`, so
Django's `reverse` needs the version as a kwarg. Tests import this wrapper
instead of `django.urls.reverse`, which keeps a version bump a
`settings.API_VERSION` change rather than an edit across every test.
"""

from django.conf import settings
from django.urls import reverse as django_reverse


def reverse(viewname: str, kwargs: dict[str, object] | None = None) -> str:
    """Reverse `viewname` at the version the service currently serves."""
    return django_reverse(viewname, kwargs={"version": settings.API_VERSION, **(kwargs or {})})
