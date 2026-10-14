#!/usr/bin/env python
"""Check a running server: the login, the dressed surfaces, a form.

A live check, so a script and not a test - it needs a server and a socket, and
`docs/TESTING.md` keeps those out of the suite. Run it after changing anything
that serves:

    uv run scaffolding runserver &
    uv run python bin/serve_smoke.py

Stdlib only: a smoke that runs on a bare `uv sync` proves the runtime set is
what it claims. `--email` picks whose session to forge; the default is the only
account when there is one.
"""

import argparse
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
    """A session for a real account."""
    accounts = BaseUser.objects.filter(email=email) if email else BaseUser.objects.all()[:2]
    found = list(accounts)
    if len(found) != 1:
        sys.exit(f"Pick an account with --email; found {len(found)}.")
    person = found[0]
    store = import_module(settings.SESSION_ENGINE).SessionStore()
    store.create()
    store["_auth_user_id"] = str(person.pk)
    store["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
    store["_auth_user_hash"] = person.get_session_auth_hash()
    store.save()
    return str(store.session_key)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url: str, cookie: str = "") -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"Cookie": cookie} if cookie else {})
    try:
        with OPENER.open(request, timeout=10) as answer:
            return answer.status, answer.read()
    except urllib.error.HTTPError as answer:
        return answer.code, answer.read()
    except OSError as unreachable:
        print(f"    {unreachable}")
        return -1, b""


def status(url: str, cookie: str = "") -> int:
    return fetch(url, cookie)[0]


def carries(url: str, cookie: str, needle: bytes) -> bool:
    return needle in fetch(url, cookie)[1]


# The dressed surfaces: the pages that wear the shared chrome.
DRESSED = ("/", "/notes/")


def dressed(base: str, cookie: str) -> bool:
    for path in DRESSED:
        body = fetch(f"{base}{path}", cookie)[1]
        if body.count(b"<footer") != 1 or body.count(b'aria-label="Principal"') != 1:
            print(f"    {path}: {body.count(b'<footer')} footers, {body.count(b'aria-label="Principal"')} navs")
            return False
    return True


def main(base: str, cookie: str) -> None:
    print("anonymous:")
    report("the login page answers", status(f"{base}/login/") == 200)
    report("the home page sends you to login", status(f"{base}/") == 302)
    report("notes refuse a stranger", status(f"{base}/notes/") == 302)
    report("static files are served", status(f"{base}/static/admin/css/base.css") == 200)

    print("logged in:")
    report("the home page renders", status(f"{base}/", cookie) == 200)
    report("notes render", status(f"{base}/notes/", cookie) == 200)
    report("the api answers", status(f"{base}/api/v1.0/", cookie) == 200)
    report("every page carries the chrome", dressed(base, cookie))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://localhost:8000")
    parser.add_argument("--email", default="", help="whose session to forge; the default is the only account")
    options = parser.parse_args()
    main(options.base.rstrip("/"), f"sessionid={session_for(options.email)}")
    sys.exit(f"\n{len(FAILURES)} failed: {', '.join(FAILURES)}" if FAILURES else "\nall good")
