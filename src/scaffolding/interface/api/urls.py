"""The versioned API's URLconf: every viewset in `VIEWS`, routed.

The router is built here and not kept in a module of its own. It held one
`DefaultRouter()` that this file imported and then registered into, so the
URLconf depended on nobody else having registered into it first.
"""

from django.urls import URLPattern, URLResolver
from rest_framework.routers import DefaultRouter

from scaffolding.service.views import VIEWS


def build_urls() -> list[URLPattern | URLResolver]:
    router = DefaultRouter()
    for prefix, viewset, basename in VIEWS:
        router.register(prefix, viewset, basename=basename)
    # A `dj_rest_auth` include sat here until 2026-09-18, mounting a password
    # login no account in this tool has a password for. See docs/ARCHITECTURE.md.
    return list(router.urls)


urlpatterns = build_urls()
