"""The OpenAPI document is generated, so its warnings are the gate on it."""

import os

from django.core.management import call_command


def test_the_schema_generates_without_warnings():
    """drf-spectacular names an enum component after the first field that uses the
    choice set, so several fields sharing one produce a name that moves when
    generation order does - seven fields share Currency.choices under three
    attribute names. `--fail-on-warn` exits nonzero, which fails this test.
    """
    call_command("spectacular", "--file", os.devnull, "--fail-on-warn")
