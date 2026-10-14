"""The wire shapes, in one place.

A resource whose wire shape carries a rule keeps its own module; the rest say
nothing but "this model, every field", so they are a table - see `base.plain`.

`PLAIN` is keyed by model rather than by name: `service/views.py` already knows
the model it is routing, and a second spelling of the same noun is a second thing
to keep in step.
"""

from django.db import models
from rest_framework import serializers

from ..models import Note
from .base import plain

PLAIN: dict[type[models.Model], type[serializers.ModelSerializer]] = {Note: plain(Note)}

WITH_RULES: dict[type[models.Model], type[serializers.ModelSerializer]] = {}


def of(model: type[models.Model]) -> type[serializers.ModelSerializer]:
    """The serializer for `model`, whether it carries a rule or not."""
    return WITH_RULES.get(model) or PLAIN[model]


__all__ = ["PLAIN", "WITH_RULES", "of"]
