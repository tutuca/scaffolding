"""What the API's own description says about a model, for the UI to read.

`/api/schema/` is generated from the serializers: for every model they expose it holds each
field's label (`title`), hint (`description`), kind (`type` and `format`), size
(`maxLength`), whether it may be empty (`nullable`), its values (`enum`) and whether a
person can write it (`readOnly`). That is the contract this app's forms and tables want,
already written, in a form the browser can read as well as Python. This module only finds
a model's component in it; nothing is copied.

The component is named for the model (`Goal`), which is how `service/views.py` registers the
serializers. A model with no endpoint has no component - a read model has none, for example -
and asking for it is an error, not an empty answer.
"""

from functools import lru_cache
from typing import cast

from django.db import models
from drf_spectacular.generators import SchemaGenerator

type Property = dict[str, object]
type Component = dict[str, object]


@lru_cache(maxsize=1)
def components() -> dict[str, Component]:
    """Every component of the schema, generated once: it is the code's own, and does not change
    while the process runs."""
    return dict(SchemaGenerator().get_schema(request=None, public=True)["components"]["schemas"])


def schema_of(model: type[models.Model]) -> Component:
    return components()[model.__name__]


def properties(component: Component) -> dict[str, Property]:
    return cast(dict[str, Property], component["properties"])


def kind_of(prop: Property) -> str:
    """What a column of this field is: `number`, `date`, or `text` - the three a table sorts by."""
    if prop.get("type") in {"integer", "number"} or prop.get("format") == "decimal":
        return "number"
    if prop.get("format") in {"date", "date-time"}:
        return "date"
    return "text"
