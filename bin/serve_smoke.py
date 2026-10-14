#!/usr/bin/env python
"""Check a running server: the gate, every dressed surface, a form.

A live check, so a script and not a test - it needs a server and a socket, and
`docs/TESTING.md` keeps those out of the suite. Run it after changing anything
that serves:

    uv run scaffolding runserver &
    uv run python bin/serve_smoke.py

Stdlib only: a smoke that runs on a bare `uv sync` proves the runtime set is
what it claims.

`--email` picks whose session to forge; the default is the only account when
there is one. Forging is the point: the alternative is a Google round trip,
which a smoke check cannot make.
"""

import argparse
import http.cookies
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from importlib import import_module

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scaffolding.conf.settings")
django.setup()

from django.conf import settings  # noqa: E402  - django.setup() has to run first

from scaffolding.data.models import BaseUser  # noqa: E402

FAILURES: list[str] = []


def report(what: str, ok: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if ok else 'FAIL'}  {what}{f' - {detail}' if detail else ''}")
    if not ok:
        FAILURES.append(what)


def session_for(email: str) -> str:
    """A session for a real account, written the way `login` writes one."""
    accounts = BaseUser.objects.filter(email=email) if email else BaseUser.objects.all()[:2]
    found = list(accounts)
    if len(found) != 1:
        sys.exit(f"Elegí una cuenta con --email; hay {len(found)}.")
    person = found[0]
    store = import_module(settings.SESSION_ENGINE).SessionStore()
    store.create()
    store["_auth_user_id"] = str(person.pk)
    store["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
    store["_auth_user_hash"] = person.get_session_auth_hash()
    store.save()
    return str(store.session_key)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """A 302 is an answer this smoke asserts on, not a hop to follow."""

    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url: str, cookie: str = "", data: bytes | None = None) -> tuple[int, bytes, dict[str, str]]:
    request = urllib.request.Request(url, data=data, headers={"Cookie": cookie} if cookie else {})
    try:
        with OPENER.open(request, timeout=10) as answer:
            return answer.status, answer.read(), dict(answer.headers)
    except urllib.error.HTTPError as answer:
        return answer.code, answer.read(), dict(answer.headers)
    except OSError as unreachable:
        print(f"    {unreachable}")
        return -1, b"", {}


def status(url: str, cookie: str = "") -> int:
    return fetch(url, cookie)[0]


def carries(url: str, cookie: str, needle: bytes) -> bool:
    """Whether a page's body contains `needle`. A status check cannot see a
    figure that drew nothing or a stylesheet that lost its link."""
    return needle in fetch(url, cookie)[1]


# Every surface that should wear the chrome. There is no `/notebooks/` shelf:
# the nav links the two books directly, and the route was retired with it.
DRESSED = (
    "/",
    "/notebooks/movimientos",
    "/notebooks/inversiones",
    "/notebooks/planes",
    "/certificado",
    "/data/invoice/",
)


def dressed(base: str, cookie: str) -> bool:
    """One nav and one footer on each surface. Counted rather than merely
    found: nesting our footer inside the admin's own produced two once, which
    a presence check cannot see."""
    for path in DRESSED:
        body = fetch(f"{base}{path}", cookie)[1]
        if body.count(b"<footer") != 1 or body.count(b'aria-label="Principal"') != 1:
            print(f"    {path}: {body.count(b'<footer')} footers, {body.count(b'aria-label="Principal"')} navs")
            return False
    return True


def posts(url: str, cookie: str) -> bool:
    """Whether the register form posts through: 200 is the form coming back
    with its errors, which is Django answering."""
    _, _, headers = fetch(url, cookie)
    jar = http.cookies.SimpleCookie()
    jar.load(headers.get("Set-Cookie", ""))
    token = jar["csrftoken"].value if "csrftoken" in jar else ""
    body = urllib.parse.urlencode({"csrfmiddlewaretoken": token, "tax_id": "", "punto_venta": ""}).encode()
    code, _, _ = fetch(url, f"{cookie}; csrftoken={token}", data=body)
    return code == 200


def main(base: str, cookie: str) -> None:
    print("anonymous:")
    report("the gateway answers", status(f"{base}/accounts/login/") == 200)
    report("the admin sends you to a login", status(f"{base}/") == 302)
    report("notebooks refuse a stranger", status(f"{base}/notebooks/") == 302)
    report("static files are served", status(f"{base}/static/admin/css/base.css") == 200)

    print("logged in:")
    report("the home page renders", status(f"{base}/", cookie) == 200)
    report("the api answers", status(f"{base}/api/v1.0/", cookie) == 200)
    # The figures draw client-side since the books graduated, so the server can
    # only assert the mount point each one lands on - a browser is what proves
    # the SVG (`bin/ui_shot.py`). A whole-body `<svg` never appears in the HTML.
    report("movimientos mounts its figures", carries(f"{base}/notebooks/movimientos", cookie, b'data-chart="split"'))
    report(
        "inversiones mounts its dashboard",
        carries(f"{base}/notebooks/inversiones", cookie, b'data-chart="strategies_bars"'),
    )
    report("every page carries the chrome", dressed(base, cookie))
    report("a form posts to django", posts(f"{base}/", cookie))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://localhost:8000")
    parser.add_argument("--email", default="", help="whose session to forge; the default is the only account")
    options = parser.parse_args()
    main(options.base.rstrip("/"), f"sessionid={session_for(options.email)}")
    sys.exit(f"\n{len(FAILURES)} fallaron: {', '.join(FAILURES)}" if FAILURES else "\ntodo bien")
