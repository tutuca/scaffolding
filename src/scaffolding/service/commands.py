"""What the command line exposes, mirroring `views.py` for HTTP.

This table wires nothing: Django discovers management commands by filename under
`interface/cli/management/commands/`. It is here so the two interfaces can be
read side by side - `views.py` says what HTTP serves, this says what argv serves,
and both point at the same use cases underneath.

`tests/scaffolding/test_conventions.py` asserts the table and the command modules
agree, so it is checked documentation rather than a comment that rots.
"""

from .domain.notes import use_cases as notes

# (command name, the use cases the command binds). References for a reader to
# follow, never invoked from here.
COMMANDS: list[tuple[str, tuple[object, ...]]] = [
    ("notes", (notes.create_note, notes.list_notes)),
]
