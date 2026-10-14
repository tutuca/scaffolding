"""Base command for everything under `management/commands/`.

One thing, the same one the API viewset does for HTTP: a refusal from the domain
is what the operator did, not a bug, so it prints as a message instead of a
traceback.
"""

from django.core.management.base import BaseCommand, CommandError, CommandParser

from scaffolding.data.models import Tenant
from scaffolding.exceptions import DomainRefusal


class ScaffoldingCommand(BaseCommand):
    def create_parser(self, prog_name: str, subcommand: str, **kwargs: object) -> CommandParser:
        """Every command takes `--tenant`, added here rather than in each
        `add_arguments`: a flag every command needs should not depend on each
        remembering."""
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser.add_argument("--tenant", default="", help="Slug of the tenant to operate on.")
        return parser

    def execute(self, *args: object, **options: object) -> str | None:
        try:
            return super().execute(*args, **options)
        except DomainRefusal as failure:
            raise CommandError(str(failure)) from None

    def tenant(self, slug: str = "") -> int:
        """Which tenant this command acts on, as the id an entry point takes.

        `--tenant` names it by slug. With no flag and exactly one tenant, that
        one is meant; with several and no flag there is no right answer to guess.
        """
        if slug:
            found = Tenant.objects.filter(slug=slug).values_list("pk", flat=True).first()
            if found is None:
                raise CommandError(f"No tenant with slug {slug}.")
            return found
        registered = list(Tenant.objects.values_list("pk", flat=True)[:2])
        if not registered:
            raise CommandError("No tenant registered. Register one first.")
        if len(registered) > 1:
            known = ", ".join(Tenant.objects.values_list("slug", flat=True))
            raise CommandError(f"More than one tenant; pick one with --tenant ({known}).")
        return registered[0]
