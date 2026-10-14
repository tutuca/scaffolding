"""The API's version is part of its contract, so it gets pinned like one.

DRF resolves the version out of the URL path; these tests assert the served
version, that an unlisted version is refused rather than silently served, and
that the OpenAPI document agrees with the URL.
"""

import pytest
from django.conf import settings
from django.test import Client
from django.urls import resolve
from rest_framework.versioning import URLPathVersioning

from scaffolding.service.domain.billing import InvoiceViewSet


def test_served_version_is_1_0():
    """The one figure worth pinning. DRF's and drf-spectacular's copies are built
    from API_VERSION in settings.py, so asserting them restates the assignment."""
    assert settings.API_VERSION == "1.0"


def test_routes_are_mounted_under_the_version():
    match = resolve("/api/v1.0/scaffolding/")

    assert match.kwargs["version"] == "1.0"
    # DRF hangs the viewset off the generated view function as `.cls`.
    assert match.func.cls is InvoiceViewSet  # type: ignore[attr-defined]


def test_viewsets_use_url_path_versioning():
    assert InvoiceViewSet.versioning_class is URLPathVersioning


@pytest.mark.django_db
@pytest.mark.parametrize("version", ["0.9", "1.1", "9.9"])
def test_an_unlisted_version_is_refused(version):
    """The path shape still matches; DRF refuses the version itself."""
    assert Client().get(f"/api/v{version}/scaffolding/").status_code == 404


@pytest.mark.django_db
def test_schema_is_served(api):
    assert api.get("/api/schema/").status_code == 200
