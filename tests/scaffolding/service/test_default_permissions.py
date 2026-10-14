"""The configured default must survive the suite's shared fixture setup.

This minimal endpoint deliberately inherits the application's DRF settings.
A session-wide permission mock previously admitted anonymous requests here.
"""

import pytest
from django.urls import path
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework.views import APIView

from scaffolding.data.models import BaseUser


class ProtectedView(APIView):
    def get(self, request: Request) -> Response:
        return Response({"admitted": True})


urlpatterns = [path("protected/", ProtectedView.as_view())]

pytestmark = [pytest.mark.django_db, pytest.mark.urls(__name__)]


def test_default_permissions_refuse_an_anonymous_request() -> None:
    assert APIClient().get("/protected/").status_code == 401


def test_default_permissions_accept_a_real_session(owner: BaseUser) -> None:
    client = APIClient()
    client.force_login(owner)

    assert client.get("/protected/").json() == {"admitted": True}
