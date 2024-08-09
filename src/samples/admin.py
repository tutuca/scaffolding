from django.contrib import admin

from . import models


class SampleAdmin(admin.ModelAdmin):
    list_filter = [
        "id",
        "title",
    ]
    search_fields = ["title"]


class SampleInline(admin.TabularInline):
    model = models.Sample
    extra = 1


class SampleTypeAdmin(admin.ModelAdmin):
    list_filter = [
        "id",
        "name",
    ]
    search_fields = ["name"]
    inlines = [
        SampleInline,
    ]


# Register your models here.
admin.site.register(models.Sample, SampleAdmin)
admin.site.register(models.SampleType, SampleTypeAdmin)
