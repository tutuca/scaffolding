"""What each role may do, per resource.

Django's own vocabulary - the four actions it makes a `Permission` row for -
resolved against the membership instead of `user.user_permissions`, because the
answer depends on which books the row is in.

Minimal by default: a resource absent from a role's row is invisible to it, and
`test_conventions.py` fails until a new model is classified.
"""

from scaffolding.data.enums import Role

# Django's four, named so the codenames line up: `data.change_invoice`.
VIEW, ADD, CHANGE, DELETE = "view", "add", "change", "delete"

READ = frozenset({VIEW})
WRITE = frozenset({VIEW, ADD, CHANGE, DELETE})
# Reference data is read by everyone and written by `scaffolding loadreference`.
SHARED = READ

# A grant on the root carries to what it contains: an invoice's lines are part
# of the invoice, not a second thing to hand out.
CONTAINED_BY = {
    "invoiceline": "invoice",
    "reversalentry": "invoice",
    "accountbalance": "account",
    "settlement": "account",
    # The three proxy readings of one movements table.
    "payment": "movement",
    "expense": "movement",
    "untriaged": "movement",
    # A bill explains a movement: what the money was for.
    "bill": "movement",
}

# Public facts. Every member reads them; nobody writes them through a role.
REFERENCE = {
    "monotributoscale",
    "legalthreshold",
    "exchangerate",
    "compensatoryrate",
    "autonomoscontribution",
    "categorygroup",
    "investmentplankind",
    "priceindex",
    "marketindex",
    "laborindex",
}

VISIBILITY: dict[str, dict[str, frozenset[str]]] = {
    Role.OWNER: {
        "client": WRITE,
        "contract": WRITE,
        "account": WRITE,
        "cutoff": WRITE,
        "invoice": WRITE,
        "movement": WRITE,
        "goal": WRITE,
        "obligation": WRITE,
        "investmentplan": WRITE,
        # How their statements and bills are read, and what they have declared: the owner's own setup.
        "categoryrule": WRITE,
        "categoryoverride": WRITE,
        "billissuer": WRITE,
        "parameter": WRITE,
        "result": READ,
        "monotributostatus": WRITE,
        # Their own books: the CUIT, the certificate, and who else may act on them.
        "taxpayer": frozenset({VIEW, CHANGE}),
        "membership": WRITE,
    },
    Role.ACCOUNTANT: {
        # The fiscal ledger, and only that. A contador needs the comprobantes and
        # the movements behind them; what someone is saving for, and by when, is
        # not part of the job and is the clearest case for this table existing.
        "client": READ,
        "contract": READ,
        "account": READ,
        # Closing a period is the job: it is the contador who decides that August
        # is reported and will not move again.
        "cutoff": WRITE,
        "invoice": WRITE,
        "movement": WRITE,
        "monotributostatus": WRITE,
        "taxpayer": READ,
    },
    Role.VIEWER: {
        "client": READ,
        "contract": READ,
        "account": READ,
        # Whether a figure is final is part of reading it.
        "cutoff": READ,
        "invoice": READ,
        "movement": READ,
        "goal": READ,
        "obligation": READ,
        "investmentplan": READ,
        "result": READ,
        "monotributostatus": READ,
        "taxpayer": READ,
    },
}


def root_of(model_name: str) -> str:
    """The resource a grant is written against."""
    return CONTAINED_BY.get(model_name, model_name)


def allows(role: str | None, model_name: str, action: str) -> bool:
    """Whether `role` may take `action` on `model_name`. No role allows nothing."""
    if role is None:
        return False
    resource = root_of(model_name)
    if resource in REFERENCE:
        return action in SHARED
    return action in VISIBILITY.get(role, {}).get(resource, frozenset())
