"""Reading a Google OAuth client out of the JSON Google hands you."""

import json
from pathlib import Path

# Google names the wrapper key after the client's type. Both hold the same pair.
KINDS = ("web", "installed")

NONE = {"client_id": "", "secret": ""}


def client_credentials(path: str | Path) -> dict[str, str]:
    """The id and secret from a client file.

    Empty when the file is absent or is not a client: a fresh clone has neither
    and still has to import settings. What refuses is the door itself.
    """
    location = Path(path)
    if not location.is_file():
        return NONE
    document = json.loads(location.read_text())
    for kind in KINDS:
        if kind in document:
            return {"client_id": document[kind].get("client_id", ""), "secret": document[kind].get("client_secret", "")}
    return NONE
