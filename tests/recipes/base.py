"""What every owned recipe needs: a taxpayer, and parents that share it.

A row whose parent belongs to different books is a row the factories refuse, so
a recipe that baked one would be testing against a state the application cannot
reach. `owned` builds each parent from the same taxpayer as the child, which is
also what makes a cross-taxpayer test have to say so explicitly.
"""

from functools import partial
from typing import Protocol

from django.db.models import Model
from model_bakery.recipe import Recipe

from scaffolding.data.models import Taxpayer


class Maker[M: Model](Protocol):
    """A `make_<model>` factory: field overrides in, one saved row out."""

    def __call__(self, **fields: object) -> M: ...


def owned[M: Model](recipe: Recipe[M], taxpayer: Taxpayer, **parents: Maker[Model]) -> Maker[M]:
    """A `make_*` that defaults the taxpayer, and builds parents in the same books.

    A parent is only built when the caller did not supply one - otherwise every
    call would leave an orphan row behind.
    """
    make: Maker[M] = partial(recipe.make)

    def build(**fields: object) -> M:
        fields.setdefault("taxpayer", taxpayer)
        for name, make_parent in parents.items():
            if name not in fields:
                fields[name] = make_parent(taxpayer=fields["taxpayer"])
        return make(**fields)

    return build
