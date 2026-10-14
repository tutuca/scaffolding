"""Base command for everything under `management/commands/`.

One thing, the same one `ScaffoldingModelViewSet` does for HTTP: a refusal from the
domain or a failure talking to ARCA is what the operator did or what ARCA said,
not a bug, so it prints as a message instead of a traceback from three layers
down. Mapping it here keeps the commands free of the same four-clause `except`
ladder repeated at the top of every `handle`.

The same file holds the two reads every command makes the same way - which
books it is acting on, and a `YYYY-MM` month - because several commands
hand-copied each of them.

The active contract and the punto de venta were two more until rule 7. Both were
domain rules living on the CLI, so a viewset or an admin action would each have
needed their own copy; they are `billing.use_cases.active_contract` and
`billing.use_cases.punto_venta` now, and nothing here knows them.
"""

from datetime import date

from django.core.management.base import BaseCommand, CommandError, CommandParser

from scaffolding.data.models import BaseUser, Taxpayer
from scaffolding.exceptions import DomainRefusal
from scaffolding.interface.adapter import AdapterError
from scaffolding.interface.cli import credentials


def exclusive(options: dict[str, object], *names: str) -> None:
    """Reject competing actions, including Django's keyword-only invocations."""
    chosen = [
        f"--{name.replace('_', '-')}"
        for name in names
        if (value := options.get(name)) is not None and value is not False and value != ""
    ]
    if len(chosen) > 1:
        raise CommandError(f"Usá uno solo de {', '.join(chosen)}.")


def since_until(since: date, until: date) -> None:
    """Refuse a range whose end precedes its start, in the operator's words.

    `catchup` and `crosswalk` each wrote the sentence; one spelling for one
    refusal."""
    if until < since:
        raise CommandError(f"--until {until:%Y-%m} es anterior a --since {since:%Y-%m}.")


class ScaffoldingCommand(BaseCommand):
    def create_parser(self, prog_name: str, subcommand: str, **kwargs: object) -> CommandParser:
        """Every command takes `--taxpayer`, added here rather than in each
        `add_arguments`: several commands use subparsers and do not call super(),
        and a flag every command needs should not depend on each remembering."""
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser.add_argument("--taxpayer", default="", help="CUIT del contribuyente sobre el que operar.")
        return parser

    def execute(self, *args: object, **options: object) -> str | None:
        # Wrapped around `execute` rather than `handle`, so a command overrides
        # `handle` the way Django documents and inherits this for free.
        try:
            return super().execute(*args, **options)
        except (DomainRefusal, AdapterError) as failure:
            raise CommandError(str(failure)) from None

    def taxpayer(self, cuit: str = "") -> int:
        """Which books this command acts on, as the id an entry point takes.

        `--taxpayer` names them. With no flag and exactly one registered
        taxpayer, that one is meant - the single-taxpayer install, which is every
        install until someone invites a second. With several and no flag there is
        no right answer to guess at, so it refuses and says which exist.

        Identity - *who* is running this - is a separate question, answered by
        the cached credential `scaffolding login` writes. Until that lands, an
        install with one taxpayer needs neither.
        """
        if cuit:
            found = Taxpayer.objects.filter(tax_id=cuit.replace("-", "")).values_list("pk", flat=True).first()
            if found is None:
                raise CommandError(f"No hay ningún contribuyente con CUIT {cuit}.")
            return found
        registered = list(Taxpayer.objects.values_list("pk", flat=True)[:2])
        if not registered:
            raise CommandError("No hay ningún contribuyente registrado. Registrá un CUIT primero.")
        if len(registered) > 1:
            known = ", ".join(Taxpayer.objects.values_list("tax_id", flat=True))
            raise CommandError(f"Hay más de un contribuyente; elegí uno con --taxpayer ({known}).")
        return registered[0]

    def acting_user(self) -> BaseUser:
        """Who is running this, for the commands that act as a person - writing
        to someone's Drive, say, rather than reading the ledger.

        From the cache `scaffolding login` writes. With exactly one account and no
        cache, that one is meant; with several there is no right answer to guess.
        """
        email = credentials.stored_email()
        if email:
            found = BaseUser.objects.filter(email=email).first()
            if found is None:
                raise CommandError(f"{email} está en las credenciales pero no tiene cuenta acá.")
            return found
        accounts = list(BaseUser.objects.all()[:2])
        if not accounts:
            raise CommandError("No hay ninguna cuenta. Creá una con `scaffolding createsuperuser`.")
        if len(accounts) > 1:
            raise CommandError("Hay más de una cuenta; identificate con `scaffolding login`.")
        return accounts[0]

    def month(self, value: str) -> date | None:
        """`YYYY-MM` → the first of that month; empty → None; anything else refuses."""
        if not value:
            return None
        try:
            year, month = (int(part) for part in value.split("-"))
            return date(year, month, 1)
        except ValueError, TypeError:
            raise CommandError(f"Expected YYYY-MM, got {value!r}.") from None
