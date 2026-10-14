"""The tenant admin: the workspace itself, with its memberships inline."""

from django.contrib import admin

from ..models.membership import Membership
from ..models.tenant import Tenant


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    fields = ("user", "role", "invited_by")


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "updated_on")
    search_fields = ("name", "slug")
    inlines = [MembershipInline]
