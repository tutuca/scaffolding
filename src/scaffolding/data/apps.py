from importlib import import_module

from django.apps import AppConfig


class DataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scaffolding.data"
    label = "data"

    def ready(self) -> None:
        # Imported for effect: each module under data/admin/ calls @admin.register.
        import_module("scaffolding.data.admin")
        # Same shape: the checks module calls @register (the deploy-time security
        # check). Django never imports app checks modules itself.
        import_module("scaffolding.data.checks")
