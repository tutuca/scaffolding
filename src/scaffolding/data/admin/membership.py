"""The membership admin."""

from django.contrib import admin

from ..models.membership import Membership


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "role", "invited_by")
    list_filter = ("role",)
    search_fields = ("user__email", "tenant__name")
