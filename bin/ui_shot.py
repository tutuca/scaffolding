#!/usr/bin/env python
"""Shots of every dressed surface, for eyes about to claim "done".

Drives the system Chrome headless over the DevTools protocol with tornado's
websocket client. Tornado is a `dev` dependency for exactly this: it is a dev-box
tool, and the dev box has the extra. The
session is forged the way `serve_smoke.py` forges one, imported from there:
`sys.path[0]` is `bin/` when this file runs as the script.

Two widths per surface: 360 is a phone, 1280 is the laptop this tool lives on.
`var/shots/` is gitignored with the rest of `var/`; before/after is two runs
with a `git stash` between them. A change under `ui/` is not done until these
have been rendered and looked at - `docs/DESIGN.md`, "the method".
"""

import argparse
import asyncio
import base64
import json
import subprocess
import tempfile
import time
from itertools import count
from pathlib import Path

from django.conf import settings
from serve_smoke import session_for
from tornado.httpclient import AsyncHTTPClient
from tornado.websocket import WebSocketClientConnection, websocket_connect

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Surface name, path, whether the shot is of a session or of a stranger.
# The login page is shot anonymous: with a session it would be a redirect.
SURFACES = [
    ("home", "/", True),
    ("login", "/login/", False),
    ("notes", "/notes/", True),
    ("colophon", "/colophon/", True),
]
# A page in a state the shot of the page alone does not show: a script run once the page has
# settled, the seconds to wait for what it set going, and a shot of the viewport (a dialog is
# over the page, not part of its length). Only with scripting on.
CLICK = "document.querySelector('{}').click()"
# Pick the first row up with the keyboard, move it one place, drop it: the order's bar appears.
MOVE = (
    "(() => { const h = document.querySelector('[data-handle]'); h.focus();"
    " for (const k of [' ', 'ArrowDown', ' ']) h.dispatchEvent(new KeyboardEvent('keydown', {key: k, bubbles: true})); })()"
)
STATES: list[tuple[str, str, str, float]] = []
WIDTHS = [360, 1280]

IDS = count(1)


def devtools_port(profile: Path) -> int:
    """Chrome writes the port it chose to `DevToolsActivePort`; wait for it."""
    marker = profile / "DevToolsActivePort"
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if marker.is_file() and marker.read_text().strip():
            return int(marker.read_text().splitlines()[0])
        time.sleep(0.1)
    raise RuntimeError("chrome never wrote DevToolsActivePort")


async def call(ws: WebSocketClientConnection, method: str, params: dict[str, object] | None = None) -> dict:
    """One CDP command, skipping the event chatter until our answer arrives."""
    ident = next(IDS)
    await ws.write_message(json.dumps({"id": ident, "method": method, "params": params or {}}))
    while True:
        raw = await ws.read_message()
        if raw is None:
            raise RuntimeError(f"chrome hung up during {method}")
        answer = json.loads(raw)
        if answer.get("id") == ident:
            if "error" in answer:
                raise RuntimeError(f"{method}: {answer['error']}")
            return dict(answer.get("result", {}))


async def settled(ws: WebSocketClientConnection, scripts: bool = True) -> None:
    """Loaded and mounted, not just loaded.

    `main.js` lazy-loads the figures after the document is complete - the
    vendored Plot, then the renderers, then the marks - so a readyState check
    alone would shoot a page whose charts have not drawn yet. Poll until every
    mount has drawn (or the page has none), then a beat."""
    for _ in range(100):
        state = await call(ws, "Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
        if state["result"]["value"] == "complete":
            break
        await asyncio.sleep(0.1)
    drawn = (
        "[...document.querySelectorAll('[data-chart]')].every((n) => n.querySelector('svg'))"
        " && (!document.querySelector('spending-telescope')"
        "     || customElements.get('spending-telescope'))"
    )
    for _ in range(100 if scripts else 0):
        state = await call(ws, "Runtime.evaluate", {"expression": drawn, "returnByValue": True})
        if state["result"]["value"]:
            break
        await asyncio.sleep(0.1)
    await asyncio.sleep(0.3)


async def shoot(base: str, session: str, port: int, *, scripts: bool, only: set[str], out: Path) -> None:
    shots = out
    shots.mkdir(parents=True, exist_ok=True)
    client = AsyncHTTPClient()
    opened = await client.fetch(
        f"http://127.0.0.1:{port}/json/new?about:blank",
        method="PUT",
        body=b"",
        allow_nonstandard_methods=True,
    )
    ws = await websocket_connect(json.loads(opened.body)["webSocketDebuggerUrl"])
    await call(ws, "Network.enable")
    # What a page is without its script: the document the server rendered, which is
    # the version every feature promises to work in.
    await call(ws, "Emulation.setScriptExecutionDisabled", {"value": not scripts})
    for name, path, carries_session in SURFACES:
        if only and name not in only:
            continue
        # `Network.setCookie`, not a `Cookie` header through
        # `setExtraHTTPHeaders`: Chrome silently drops the latter, and
        # every authenticated shot came back as the login page.
        await call(ws, "Network.clearBrowserCookies")
        if carries_session:
            await call(
                ws,
                "Network.setCookie",
                {"name": settings.SESSION_COOKIE_NAME, "value": session, "url": f"{base}{path}"},
            )
        for width in WIDTHS:
            await call(
                ws,
                "Emulation.setDeviceMetricsOverride",
                {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": False},
            )
            await call(ws, "Page.navigate", {"url": f"{base}{path}"})
            await settled(ws, scripts)
            shot = await call(ws, "Page.captureScreenshot", {"captureBeyondViewport": True})
            target = shots / f"{name}-{width}{'' if scripts else '-nojs'}.png"
            target.write_bytes(base64.b64decode(shot["data"]))
            print(f"  {target}")
    for name, path, script, wait in STATES if scripts else []:
        if only and name not in only:
            continue
        await call(ws, "Network.clearBrowserCookies")
        await call(
            ws, "Network.setCookie", {"name": settings.SESSION_COOKIE_NAME, "value": session, "url": f"{base}{path}"}
        )
        for width in WIDTHS:
            await call(
                ws,
                "Emulation.setDeviceMetricsOverride",
                {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": False},
            )
            await call(ws, "Page.navigate", {"url": f"{base}{path}"})
            await settled(ws)
            await call(ws, "Runtime.evaluate", {"expression": script})
            await asyncio.sleep(wait)
            shot = await call(ws, "Page.captureScreenshot", {})
            target = shots / f"{name}-{width}.png"
            target.write_bytes(base64.b64decode(shot["data"]))
            print(f"  {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://localhost:8000")
    parser.add_argument("--email", default="", help="whose session to forge; the default is the only account")
    parser.add_argument("--out", default="var/shots", help="where the shots go; var/shots-baseline is the baseline")
    parser.add_argument("--no-js", action="store_true", help="shoot the pages with scripting disabled")
    parser.add_argument("--only", default="", help="comma-separated surface names; default is all")
    options = parser.parse_args()
    # Chrome and the session both come up before the event loop: the ORM
    # raises `SynchronousOnlyOperation` from an async context - the smoke's
    # rule - and launching or polling a process from a coroutine blocks it.
    with tempfile.TemporaryDirectory() as chrome_profile:
        browser = subprocess.Popen(
            [
                CHROME,
                "--headless=new",
                f"--user-data-dir={chrome_profile}",
                "--remote-debugging-port=0",
                "--no-first-run",
                # A sandboxed dev box (workspace-write) blocks the crash reporter
                # and the component updater from writing under ~/Library, which
                # otherwise kills the headless browser mid-session.
                "--no-sandbox",
                "--disable-crash-reporter",
                "--disable-component-update",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            asyncio.run(
                shoot(
                    options.base.rstrip("/"),
                    session_for(options.email),
                    devtools_port(Path(chrome_profile)),
                    scripts=not options.no_js,
                    only=set(filter(None, options.only.split(","))),
                    out=Path(options.out),
                )
            )
        finally:
            browser.terminate()
            browser.wait(timeout=10)
