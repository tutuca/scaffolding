"""The hosts this app answers on, and the one it must not.

Google registers a redirect URI per origin, and allauth mirrors the request's
host straight into `redirect_uri`. `127.0.0.1:8000` and `localhost:8000` are the
same server and two different origins, so answering on the loopback IP starts an
OAuth flow Google refuses - with a message that names neither the cause nor the
cure. Refusing the host here names both. README says it in prose; this is the
same rule where no path can walk around it.
"""

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_the_loopback_ip_is_not_a_host_this_app_answers_on(client: Client) -> None:
    refused = client.get("/", headers={"host": "127.0.0.1:8000"})

    assert refused.status_code == 400
