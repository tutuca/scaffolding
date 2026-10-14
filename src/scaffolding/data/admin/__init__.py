"""Imported for the registration side effect: the plain table, plus the modules
whose admins carry behaviour of their own."""

from . import membership, tenant, user  # noqa: F401 - each module registers its ModelAdmin on import
from .plain import register

register()
