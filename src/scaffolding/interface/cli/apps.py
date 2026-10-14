from django.apps import AppConfig


class CliConfig(AppConfig):
    """Holds the management commands.

    An app of its own because Django only discovers commands under an installed
    app, and putting them under `data` would make the data layer import the
    service layer - the opposite of the dependency direction in
    docs/ARCHITECTURE.md. No models, so no migrations.
    """

    name = "scaffolding.interface.cli"
    label = "cli"
