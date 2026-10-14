#!/usr/bin/env python3
"""Prove a built wheel is a complete tool: install, seed, boot, refuse.

Installs the wheel from `dist/` into a throwaway venv - dependencies resolved
by uv from its cache, so repeats are offline - then runs the *installed*
`scaffolding` command four times:

- `check` - Django's checks, green on a fresh install;
- `migrate` - the models ship in the wheel;
- the server boots and `/` answers - the pages' templates and statics are in
  the wheel;
- and `runserver` refuses the insecure SECRET_KEY default - the guard holds in
  the installed shape, where no checkout `.env` can supply a key.

All state goes to `SCAFFOLDING_VAR_DIR` / `SCAFFOLDING_SECRETS_DIR` under
`tmp/dist/smoke/`, which is the decoupling an installed wheel depends on:
nothing is written into site-packages. Standard library only, like
`bin/serve_smoke.py`.
"""

import argparse
import os
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp" / "dist" / "smoke"
SECRET = "wheel-smoke-key-do-not-reuse"


def latest_wheel(dist: Path) -> Path:
    wheels = sorted(dist.glob("scaffolding-*.whl"))
    if not wheels:
        raise SystemExit(f"no wheel in {dist}/ - run `make package` first")
    return wheels[-1]


def run(arguments: list[str], *, env: dict[str, str], label: str) -> None:
    result = subprocess.run(arguments, env=env, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"FAILED: {label}\n{result.stderr}\n{result.stdout}")
    print(f"ok: {label}")


def run_uv(arguments: list[str]) -> None:
    env = {**os.environ, "UV_CACHE_DIR": os.environ.get("UV_CACHE_DIR", str(ROOT / "tmp" / "uv-cache"))}
    run(arguments, env=env, label=" ".join(arguments))


def base_env(state: Path, secrets: Path) -> dict[str, str]:
    """The installed tool's environment: state told where to live, key set."""
    env = {key: value for key, value in os.environ.items() if key != "DJANGO_SETTINGS_MODULE"}
    env["SCAFFOLDING_VAR_DIR"] = str(state)
    env["SCAFFOLDING_SECRETS_DIR"] = str(secrets)
    env["SECRET_KEY"] = SECRET
    return env


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def page_status(port: int) -> int:
    request = urllib.request.Request(f"http://127.0.0.1:{port}/", headers={"Host": "localhost"})
    with urllib.request.urlopen(request, timeout=5) as response:
        return int(response.status)


def boot_the_server(command: Path, env: dict[str, str]) -> None:
    port = free_port()
    with open(TMP / "server.log", "w") as log:
        server = subprocess.Popen(
            [str(command), "runserver", f"127.0.0.1:{port}", "--noreload"],
            env=env,
            stdout=log,
            stderr=log,
            text=True,
        )
        try:
            status = None
            for _ in range(60):
                if server.poll() is not None:
                    raise SystemExit(f"server exited early; see {TMP / 'server.log'}")
                try:
                    status = page_status(port)
                    break
                except OSError:
                    time.sleep(0.5)
            if status is None:
                raise SystemExit(f"no answer on :{port} in 30s; see {TMP / 'server.log'}")
            print(f"ok: server on :{port} answers / with {status}")
        finally:
            server.terminate()
            server.wait(timeout=10)


def refuse_the_insecure_key(command: Path, env: dict[str, str]) -> None:
    unconfigured = {key: value for key, value in env.items() if key not in {"SECRET_KEY", "DEBUG"}}
    unconfigured["DEBUG"] = "false"
    result = subprocess.run(
        [str(command), "runserver", "--noreload"],
        env=unconfigured,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        raise SystemExit("runserver served with the insecure default key - the guard is not working")
    if "SECRET_KEY" not in result.stderr + result.stdout:
        raise SystemExit(f"refused, but the message does not name SECRET_KEY:\n{result.stderr}")
    print("ok: runserver refuses the insecure default key")


def main() -> None:
    parser = argparse.ArgumentParser(description="install the built wheel and prove it boots")
    parser.add_argument("--wheel", type=Path, default=latest_wheel(ROOT / "dist"), help="default: newest in dist/")
    arguments = parser.parse_args()
    wheel: Path = arguments.wheel

    if TMP.exists():
        shutil.rmtree(TMP)
    state = TMP / "state"
    secrets = state / "secrets"
    state.mkdir(parents=True)
    secrets.mkdir()

    venv = TMP / "venv"
    run_uv(["uv", "venv", str(venv)])
    run_uv(["uv", "pip", "install", "--python", str(venv / "bin" / "python"), str(wheel)])

    command = venv / "bin" / "scaffolding"
    env = base_env(state, secrets)
    run([str(command), "check"], env=env, label="scaffolding check")
    run([str(command), "migrate"], env=env, label="scaffolding migrate")

    boot_the_server(command, env)
    refuse_the_insecure_key(command, env)

    shutil.rmtree(TMP)
    print(f"wheel smoke: {wheel.name} is a complete tool")


if __name__ == "__main__":
    main()
