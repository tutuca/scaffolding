"""One taxpayer's rows. What a role may do with them is not asked here.

`data/backends.RoleBackend` answers that, so `ModelAdmin`'s own
`has_view/add/change/delete/module_permission` need no overriding - a change from
2026-09-18, when `VisibleAdmin` and `ReferenceAdmin` went. A reference table is a
plain `ModelAdmin` now: the table grants every role `view` and nothing else, and
the backend says so without a class to carry it.

Ownership stays here, because it is a different question. `get_queryset` is what
enforces it: `ModelAdmin.get_object` resolves through that queryset, so another
taxpayer's row is a 404 on a guessed id before anything is asked. A per-object
permission would be a second answer to a settled question.
"""

from typing import cast

from django.contrib import admin
from django.db.models import ForeignKey, Model, QuerySet
from django.forms import BaseInlineFormSet, ModelChoiceField, ModelForm
from django.http import HttpRequest

from scaffolding.data.models import BaseUser, Tenant
from scaffolding.data.models.base import OwnedModel, OwnedQuerySet


def person(request: HttpRequest) -> BaseUser | None:
    """Who is looking, or None when that is nobody.

    A function and not a method, because three admin classes need it and only
    one of them is an `OwnedAdmin`: `Tenant` is a workspace rather than a row
    in one, and `Membership` is the edge.

    None for a stranger, because `AdminSite.login` builds the whole app list
    through `each_context` - so an admin is asked about a request before anybody
    has authenticated, and `AnonymousUser` carries none of what follows. See
    `tests/scaffolding/data/admin/test_logged_out.py`.
    """
    if not request.user.is_authenticated:
        return None
    return request.user


def narrow_choices(db_field: ForeignKey, request: HttpRequest, kwargs: dict[str, object]) -> None:
    """A dropdown on an owned relation offers only the active books' rows.

    The changelist narrows by books in `get_queryset`; this is the same answer
    for the change form's relations, which Django builds from the related
    model's own manager and would otherwise offer every taxpayer's rows as
    choices - and accept one on save. A superuser's form stays unnarrowed for
    the reason their changelist does.
    """
    if not issubclass(db_field.related_model, OwnedModel) or request.user.is_superuser:
        return
    looking = person(request)
    related = cast(OwnedQuerySet, db_field.related_model._default_manager.get_queryset())
    active = looking.active_tenant_id if looking else None
    kwargs["queryset"] = related.owned_by(active) if active is not None else related.none()


class OwnedInline(admin.TabularInline):
    """An inline on owned rows. Same reason as `OwnedAdmin.exclude`: a dropdown
    would list every taxpayer, including ones the person has no membership on.
    `OwnedAdmin.save_formset` fills it from the parent instead."""

    exclude = ["tenant"]

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs: object
    ) -> ModelChoiceField | None:
        narrow_choices(db_field, request, kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class OwnedAdmin(admin.ModelAdmin):
    # Which books a row lands in comes from who is looking, not a dropdown.
    exclude = ["tenant"]

    def active(self, request: HttpRequest) -> Tenant | None:
        looking = person(request)
        return looking.active_tenant if looking else None

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """What enforces ownership. The role is the backend's question."""
        queryset = cast(OwnedQuerySet, super().get_queryset(request))
        if request.user.is_superuser:
            return queryset
        books = self.active(request)
        return queryset.none() if books is None else queryset.owned_by(books.pk)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Adding is the only action needing to know which books to file under;
        view, change and delete work on rows that already name their own. Asked
        before the role, because a superuser passes that and would then be
        offered a form `save_model` can only save as null."""
        return self.active(request) is not None and super().has_add_permission(request)

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs: object
    ) -> ModelChoiceField | None:
        narrow_choices(db_field, request, kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_formset(self, request: HttpRequest, form: ModelForm, formset: BaseInlineFormSet, change: bool) -> None:
        """An inline row lands in its parent's books.

        `formset.save()` goes around the mutators, so `same_taxpayer` never sees
        these rows and this is the only place the invariant can be stated.
        """
        rows = formset.save(commit=False)
        for row in rows:
            if getattr(row, "tenant_id", None) is None:
                setattr(row, "tenant", form.instance.tenant)  # noqa: B010 - row is any owned model here
            row.save()
        for gone in formset.deleted_objects:
            gone.delete()
        formset.save_m2m()

    def save_model(self, request: HttpRequest, obj: Model, form: ModelForm, change: bool) -> None:
        """A new row belongs to the active books, never to what a form said."""
        if not change and getattr(obj, "tenant_id", None) is None:
            setattr(obj, "tenant", self.active(request))  # noqa: B010 - obj is any owned model here
        super().save_model(request, obj, form, change)
