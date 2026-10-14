"""A table's column, from what the schema says about the field.

`{% head schema "amount" %}` is the `<th>` of the `amount` column: its text is the field's
label, its `data-key` the field's name, and what the grid sorts it by and whether it is
right-aligned are the field's kind - none of it written by hand where the table is.

`{% cell schema "amount" goal.amount %}...{% endcell %}` is the `<td>` under it. The tag owns what
the kind decides - a number is right-aligned and carries its raw value for the grid to sort
by, a date carries its ISO form - and the page owns what is shown: whatever is between the
tags, which is `{{ goal.currency }} {{ goal.amount|floatformat:"0g" }}` where a number is
shown with its money, or `cumplida` where a code is shown as a word.
"""

from django import template
from django.template.base import Parser, Token
from django.template.context import Context
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from scaffolding.ui.schema import Component, kind_of, properties

register = template.Library()


@register.simple_tag
def head(component: Component, name: str) -> SafeString:
    prop = properties(component)[name]
    kind = kind_of(prop)
    # A date is a text the grid can sort: the schema's dates are ISO, which sort as written.
    return format_html(
        '<th scope="col" data-key="{}" data-sort="{}"{}>{}</th>',
        name,
        "number" if kind == "number" else "text",
        SafeString(' class="num"') if kind == "number" else "",
        prop["title"],
    )


class CellNode(template.Node):
    def __init__(
        self,
        schema: template.base.FilterExpression,
        name: template.base.FilterExpression,
        value: template.base.FilterExpression,
        shown: template.NodeList,
    ) -> None:
        self.schema, self.name, self.value, self.shown = schema, name, value, shown

    def render(self, context: Context) -> str:
        kind = kind_of(properties(self.schema.resolve(context))[self.name.resolve(context)])
        value = self.value.resolve(context)
        attrs = ' class="num"' if kind == "number" else ""
        if kind in {"number", "date"} and value not in (None, ""):
            raw = value.isoformat() if hasattr(value, "isoformat") else str(value)
            attrs += format_html(' data-value="{}"', raw)
        return format_html("<td{}>{}</td>", mark_safe(attrs), self.shown.render(context))


@register.tag("cell")
def cell(parser: Parser, token: Token) -> CellNode:
    _, schema, name, value = token.split_contents()
    shown = parser.parse(("endcell",))
    parser.delete_first_token()
    return CellNode(parser.compile_filter(schema), parser.compile_filter(name), parser.compile_filter(value), shown)
