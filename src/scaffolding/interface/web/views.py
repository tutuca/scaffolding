"""The web shell: the home page, and the sample domain's page."""

from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from scaffolding.data.models import BaseUser
from scaffolding.service.domain.notes import use_cases as notes


class HomeView(LoginRequiredMixin, View):
    """`/` - who you are and the way onward.

    Declared before `admin.site.urls` in `conf/urls.py`, so it takes the empty
    path and the admin keeps every other one.
    """

    template_name = "ui/home.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        looking = cast(BaseUser, request.user)
        return render(request, self.template_name, {"person": looking, "tenant": looking.active_tenant})


class NotesView(LoginRequiredMixin, View):
    """`/notes/` - the sample domain, over HTTP and HTML."""

    template_name = "ui/notes.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        tenant = cast(BaseUser, request.user).active_tenant
        rows = notes.list_notes(tenant=tenant.pk) if tenant else []
        return render(request, self.template_name, {"notes": rows, "tenant": tenant})

    def post(self, request: HttpRequest) -> HttpResponse:
        tenant = cast(BaseUser, request.user).active_tenant
        if tenant is None:
            return redirect("home")
        title = request.POST.get("title", "").strip()
        if title:
            notes.create_note(tenant=tenant.pk, title=title, body=request.POST.get("body", ""))
        return redirect("notes")


class ColophonView(LoginRequiredMixin, View):
    """`/colophon/` - sources and conventions in one place."""

    template_name = "ui/colophon.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)
