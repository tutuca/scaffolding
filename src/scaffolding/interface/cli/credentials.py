"""Who this machine is logged in as. Identity only - `--taxpayer` says which
books, and the two are different questions."""

import json
import os
from pathlib import Path

CREDENTIALS_PATH = Path.home() / ".config" / "scaffolding" / "credentials.json"


def remember(*, email: str) -> Path:
    """Remember what `scaffolding login` established. 0600, like the rest."""
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(json.dumps({"email": email}))
    os.chmod(CREDENTIALS_PATH, 0o600)
    return CREDENTIALS_PATH


def stored_email() -> str:
    """The cached email, or empty when nobody has logged in."""
    if not CREDENTIALS_PATH.exists():
        return ""
    return str(json.loads(CREDENTIALS_PATH.read_text()).get("email", ""))
