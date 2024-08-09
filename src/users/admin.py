from django.contrib import admin
from . import models


class UserAdmin(admin.ModelAdmin):
    pass


class ProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.User, UserAdmin)

admin.site.register(models.Profile, ProfileAdmin)
