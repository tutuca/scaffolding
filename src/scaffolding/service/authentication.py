"""The one way in over HTTP: the session, with the challenge DRF omits.

A module of its own and not a class in `tenancy.py`, for a layering reason
rather than a taste one: DRF reads `DEFAULT_AUTHENTICATION_CLASSES` from inside
`rest_framework/views.py`, so anything named there is imported while that module
is still initialising. `tenancy` imports `APIView`, which makes the cycle real -
`AccessTokenAuthentication` lived here until 2026-09-18 and carried a
`TYPE_CHECKING` import for the same reason.
"""

from drf_spectacular.authentication import SessionScheme
from rest_framework import authentication
from rest_framework.request import Request


class SessionAuthentication(authentication.SessionAuthentication):
    """DRF's, plus the header it leaves out.

    Without `authenticate_header` DRF answers 403 where it means 401: it reads
    "no authenticator offered a challenge" as "authenticated and refused". The
    JWT class supplied one until 2026-09-18; this is what is left saying it.
    """

    def authenticate_header(self, request: Request) -> str:
        return 'Session realm="scaffolding"'


class SessionCookieScheme(SessionScheme):
    """So the schema documents the way in.

    drf-spectacular matches an authenticator by exact class, not by subclass, so
    ours resolves to nothing and it warns once per operation - 93 warnings, which
    `--fail-on-warn` turns into a failed `make openapi`. Inheriting its own
    session scheme keeps the `cookieAuth` definition and only redirects the
    target. `tests/scaffolding/interface/api/test_schema.py` is the gate.
    """

    # A dotted path rather than the class beside it: `SessionScheme` assigns a
    # string literal, so that is the type a subclass may assign. The library
    # resolves either.
    target_class = "scaffolding.service.authentication.SessionAuthentication"
