from dataclasses import dataclass


@dataclass(frozen=True)
class NoteDraft:
    """What a note is made from."""

    title: str
    body: str
