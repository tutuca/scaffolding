"""The database router: the task queue lives on its own database.

`django_tasks_db` stores enqueued tasks as rows. Those rows are process state, not
books: they live on the `tasks` database (a second SQLite beside the ledger), so a
worker that crashes mid-task, or a queue that grows, can never touch or bloat the
ledger it is reading. Everything else stays on `default`.
"""

from django.db import models


class TaskRouter:
    """Route the task queue's tables to `tasks`, and nothing else."""

    route_app_labels = {"django_tasks_database"}

    def db_for_read(self, model: type[models.Model], **hints: object) -> str | None:
        if model._meta.app_label in self.route_app_labels:
            return "tasks"
        return None

    def db_for_write(self, model: type[models.Model], **hints: object) -> str | None:
        if model._meta.app_label in self.route_app_labels:
            return "tasks"
        return None

    def allow_relation(self, obj1: models.Model, obj2: models.Model, **hints: object) -> bool | None:
        if obj1._meta.app_label in self.route_app_labels or obj2._meta.app_label in self.route_app_labels:
            return False
        return None

    def allow_migrate(
        self,
        db: str,
        app_label: str,
        model_name: str | None = None,
        **hints: object,
    ) -> bool:
        if app_label in self.route_app_labels:
            return db == "tasks"
        return db == "default"
