#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys

from django.core.management import execute_from_command_line

from scaffolding.conf.serving import refuse_insecure_key


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scaffolding.conf.settings")
    if sys.argv[1:2] == ["runserver"]:
        refuse_insecure_key()
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
