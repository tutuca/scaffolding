"""Imported for the registration side effect: the plain table, plus the modules
whose admins carry behaviour of their own."""

from . import (  # noqa: F401 - each module registers its ModelAdmin on import
    invoice,
    membership,
    reversal_entry,
    settlement,
    taxpayer,
    untriaged,
    user,
)
from .plain import register

register()
