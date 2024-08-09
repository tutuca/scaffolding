import pytest
from unittest import mock
from rest_framework.permissions import IsAuthenticated


@pytest.fixture(scope="session", autouse=True)
def mock_views_permissions():
    # little util I use for testing for DRY when patching multiple objects
    def patch_permission(perm):
        return mock.patch.multiple(
            perm,
            has_permission=mock.Mock(return_value=True),
            has_object_permission=mock.Mock(return_value=True),
        )

    with (
        patch_permission(IsAuthenticated),
    ):
        yield
