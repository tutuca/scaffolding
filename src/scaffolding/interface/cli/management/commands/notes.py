"""`scaffolding notes` - the sample domain, over argv."""

from django.core.management.base import CommandParser

from scaffolding.interface.cli.base import ScaffoldingCommand
from scaffolding.service.domain.notes import use_cases


class Command(ScaffoldingCommand):
    help = "List or create notes in a tenant."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("action", choices=["list", "add"], help="list or add")
        parser.add_argument("--title", default="", help="Note title (for add)")
        parser.add_argument("--body", default="", help="Note body (for add)")

    def handle(self, *args: object, **options: object) -> None:
        tenant = self.tenant(str(options["tenant"]))
        if options["action"] == "add":
            use_cases.create_note(tenant=tenant, title=str(options["title"]), body=str(options["body"]))
            self.stdout.write("noted.")
        else:
            for note in use_cases.list_notes(tenant=tenant):
                self.stdout.write(f"{note.title} · {note.updated_on:%Y-%m-%d}")
