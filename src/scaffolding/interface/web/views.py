"""The web shell: the home page, and the door everyone arrives through.

Registration is the home page's first gap rather than a phase with an end, which
is why it is not a wizard: there is no completed state for one to arrive at, and
Client, Contract and Account already have admin pages it would duplicate.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import cast

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from scaffolding.data.models import BaseUser
from scaffolding.exceptions import DomainRefusal, refusal, unless_refused
from scaffolding.interface.web import charts
from scaffolding.interface.web.charts import pesos
from scaffolding.service.domain.access import use_cases as access
from scaffolding.service.domain.expenses import flows
from scaffolding.service.domain.expenses import use_cases as expenses
from scaffolding.service.domain.expenses.schemas import MonthFlow
from scaffolding.service.domain.inflation import calc as inflation_calc
from scaffolding.service.domain.inflation import use_cases as inflation
from scaffolding.service.domain.inflation.schemas import InflationIndex
from scaffolding.service.domain.planning import calc as planning_calc
from scaffolding.service.domain.planning import deposits
from scaffolding.service.domain.planning import use_cases as planning
from scaffolding.service.domain.savings import use_cases as savings
from scaffolding.service.domain.tax import use_cases as tax

from .forms import CertificateForm, RegisterTaxpayerForm


def admin_url(model: str) -> str:
    """`data.contract` -> the admin changelist for it.

    The domain names the model and the shell resolves where it is: a URL is an
    HTTP fact and the domain has no business holding one.
    """
    app_label, _, model_name = model.partition(".")
    return reverse(f"admin:{app_label}_{model_name}_changelist")


@dataclass(frozen=True)
class Indicator:
    """One health number with its reference beside it - the books' own
    "comparado con qué" rule, shrunk to a row."""

    question: str
    value: str
    reference: str


@dataclass(frozen=True)
class Glance:
    """What the home shows at a glance: the indicator rows, the sync dates, the
    figures and the week telescope's tree. Built together because the indicator
    rows all read the one projection; the sync dates read their own tables and
    so survive a projection the ledger refuses."""

    indicators: list[Indicator]
    figures: dict[str, object]
    weeks: dict[str, object]
    sync: list[Indicator]


def sync_status(taxpayer: int) -> list[Indicator]:
    """The last date each feeder wrote, as rows. A table with nothing loaded
    reads a dash - a gap named, never a date invented."""
    last = access.last_reads(taxpayer=taxpayer)

    def day(value: date | None, form: str) -> str:
        return f"{value:{form}}" if value else "—"

    return [
        Indicator(question="IPC", value=day(last.ipc, "%Y-%m"), reference="INDEC"),
        Indicator(question="Mercado", value=day(last.market, "%Y-%m-%d"), reference="BCRA"),
        Indicator(question="Experimento", value=day(last.experiment, "%Y-%m-%d"), reference="corrida"),
        Indicator(question="Movimientos", value=day(last.movements, "%Y-%m-%d"), reference="carga"),
    ]


def real_ingresos(index: InflationIndex | None, months: Sequence[MonthFlow]) -> list[Decimal | None] | None:
    """The flows' income deflated by the IPC, or None with no index on file."""
    if index is None:
        return None
    return inflation_calc.restate(
        [(month.period, month.ingresos) for month in months], index=dict(zip(index.months, index.values, strict=False))
    )


def ipc_carried(index: InflationIndex | None, months: Sequence[MonthFlow]) -> list[Decimal | None] | None:
    """The first month's income carried forward by the IPC, or None with no index on file."""
    if index is None or not months:
        return None
    return inflation_calc.carry(
        months[0].ingresos,
        periods=[month.period for month in months],
        index=dict(zip(index.months, index.values, strict=False)),
    )


def glance(taxpayer: int) -> Glance:
    """The health indicators the home page opens with, the sync dates and the
    figures.

    The indicator rows are composed from reads that already exist and are
    already tested - `project`, `outlook` and `tax.position` - which is why they
    live in the shell: there is no new number here, only each one put next to its
    reference. A ledger the projection refuses gets no indicator rows rather than
    an error: the gaps list below already says what to load first. The sync dates
    read their own tables, so they stay up even when the projection has nothing
    to work from. Inflation has no chart of its own: it is folded into the flows
    chart, where the income is drawn deflated beside the nominal bars.

    The home carried the taxpayer list and the admin's app list until
    2026-10-04. Neither said anything the nav does not: the active books are
    the only books, and every table is one click behind "Admin". What is here
    now is what the person asked the page for - where the money stands, and what
    came in and went out these last months.
    """
    sync = sync_status(taxpayer)
    index = unless_refused(inflation.snapshot)
    try:
        rate = expenses.rate_in_force()
        plan = expenses.project(taxpayer=taxpayer, horizon=12, rate=rate)
    except DomainRefusal:
        return Glance(indicators=[], figures={}, weeks={}, sync=sync)
    seen = flows.outlook(taxpayer=taxpayer)
    health = plan.health
    month = plan.months[0]
    committed = month.cuota + sum((charge.amount for charge in month.obligations), Decimal(0))
    rows = [
        Indicator(
            question="La partición",
            value=f"{health.needs:.0f} / {health.wants:.0f} / {health.saved:.0f}",
            reference="la regla pide 50/30/20",
        ),
        Indicator(
            question="Gasto proyectado",
            value=f"{pesos(month.baseline)}/mes",
            reference=f"sobre un ingreso de {pesos(month.income)}",
        ),
        Indicator(
            question=f"Gastado en {seen.last_month.period}",
            value=pesos(seen.last_month.egresos),
            reference=f"entraron {pesos(seen.last_month.ingresos)} · aparte, monotributo y deuda: {pesos(committed)}",
        ),
        Indicator(
            question="Gasto semanal",
            value=f"{pesos(seen.weekly_median)}/semana",
            reference=f"mediana de las últimas {len(seen.weeks)} semanas",
        ),
    ]
    today = timezone.localdate()
    queue, why_not = refusal(lambda: planning.readiness(taxpayer=taxpayer, rate=rate, as_of=today))
    if queue is None:
        landing = f"sin cola de metas: {why_not}"
    elif not queue.outcomes[0].rows:
        landing = "sin metas planeadas"
    else:
        middle = queue.outcomes[len(queue.outcomes) // 2].rows
        paid = [row for row in middle if row.sequenced and not row.wall_missed]
        landing = (
            f"{len(paid)} de {len(middle)} metas se pagan: {paid[0].title} en {paid[0].sequenced}"
            if paid
            else f"ninguna meta se alcanza antes de {queue.horizon[-1]}"
        )
    rows.append(Indicator(question="Superávit", value=f"{pesos(month.surplus)}/mes", reference=landing))
    standing = tax.position(taxpayer=taxpayer)
    if standing.excluded:
        reading = "excluido de la escala"
    elif standing.computed_category and standing.headroom_to_category_cap is not None:
        reading = f"categoría {standing.computed_category} · quedan {pesos(standing.headroom_to_category_cap)} al tope"
    else:
        reading = "sin escala cargada"
    rows.append(
        Indicator(question="Monotributo", value=f"{pesos(standing.rolling_12m_ars)} en 12 meses", reference=reading)
    )
    figures: dict[str, object] = {}
    path = flows.trajectory(
        taxpayer=taxpayer,
        held=deposits.held_savings(taxpayer=taxpayer, as_of=today),
        payments=planning_calc.payments(queue.outcomes[len(queue.outcomes) // 2].rows) if queue else None,
        interest=dict(zip(queue.horizon, queue.interest, strict=True)) if queue else None,
    )
    figures["trajectory"] = charts.fig_trajectory(
        path,
        inflation.living(taxpayer=taxpayer, periods=[month.period for month in path.months]),
        forward=savings.forward_inflation(),
    )
    if seen.moved:
        figures["flows"] = charts.fig_flows(
            seen.months,
            projected=month.baseline,
            real_ingresos=real_ingresos(index, seen.months),
            ipc=ipc_carried(index, seen.months),
        )
    weeks: dict[str, object] = {"tree": expenses.weekly_by_month(taxpayer=taxpayer).json()} if seen.moved else {}
    return Glance(indicators=rows, figures=figures, weeks=weeks, sync=sync)


GAP_PAGES = {"certificado de ARCA": "/certificado"}


class HomeView(LoginRequiredMixin, View):
    """`/` - who you are, what is missing, and the two ways onward.

    Declared before `admin.site.urls` in `conf/urls.py`, so it takes the empty
    path and the admin keeps every other one. That shadows the admin's own
    index: `reverse("admin:index")` still resolves to `/`, so the admin's
    breadcrumb lands here, and the way back in is the nav's "Admin". The app
    list was repeated on this page for that reason until 2026-10-04; it went
    with the taxpayer list, because neither told the person anything.

    Three shapes in one day. `/profile/` was a page beside the admin and gave the
    tool two homes; folding it onto the admin index gave it one, at the cost of
    an `AdminSite` subclass, a `default_site` indirection and a template that
    could not import `data.admin.base.person` without a registration cycle. This
    is the third and the cheapest: a plain view, its own template, and nothing
    subclassed.

    Its own template rather than the admin's base, because this is the product's
    front page and the admin is a tool inside it. Barebones for now - what it
    looks like is a separate question from what is on it.
    """

    template_name = "ui/home.html"

    def context(self, request: HttpRequest, form: RegisterTaxpayerForm) -> dict[str, object]:
        looking = cast(BaseUser, request.user)
        active = looking.active_taxpayer
        seen = glance(active.pk) if active else Glance(indicators=[], figures={}, weeks={}, sync=[])
        return {
            "person": looking,
            "active": active,
            # The certificate gap links its own page rather than a changelist:
            # there is nothing to upload on one. A table, searched, so the next
            # gap with a page of its own is a row in GAP_PAGES.
            "gaps": [
                {"what": gap.what, "blocks": gap.blocks, "url": GAP_PAGES.get(gap.what) or admin_url(gap.model)}
                for gap in (access.gaps(taxpayer=active.pk) if active else [])
            ],
            "form": form,
            "indicators": seen.indicators,
            "figures": seen.figures,
            "weeks": seen.weeks,
            "sync": seen.sync,
            "pesos": inflation.deflator(taxpayer=active.pk).caption if active else "",
        }

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.context(request, RegisterTaxpayerForm()))

    def post(self, request: HttpRequest) -> HttpResponse:
        form = RegisterTaxpayerForm(request.POST)
        if form.is_valid():
            try:
                access.register_taxpayer(
                    user=cast(BaseUser, request.user).pk,
                    tax_id=form.cleaned_data["tax_id"],
                    punto_venta=form.cleaned_data["punto_venta"],
                )
                return redirect("home")
            except DomainRefusal as refusal:
                # On the field, not as a 500: a CUIT somebody holds is a thing
                # the person typed, not a thing that went wrong.
                form.add_error("tax_id", str(refusal))
        return render(request, self.template_name, self.context(request, form))


class ColophonView(LoginRequiredMixin, View):
    """`/colophon/` - the sources and names the books use, in one place.

    Each book carried its own references inline: the 50/30/20 attribution, the
    pointer to `docs/BUDGET.md`, the Tufte rules, the glossary. A reader with a
    question about a source had to know which page to open. One static page
    answers all of them, and the books link here instead of citing.
    """

    template_name = "ui/colophon.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)


class AdminLoginView(View):
    """`/login/` - the admin's password form, shadowed so there is one door.

    `SOCIALACCOUNT_ONLY` removes allauth's local login and leaves this one, and
    every `admin_view` redirect sends an anonymous visitor here - so the site's
    front page opened on a username/password form, which `docs/ARCHITECTURE.md`
    says is not the way in.

    The path is shadowed in `conf/urls.py` rather than `AdminSite` subclassed:
    routes are decided there, and `admin:login` still reverses to `/login/`, so
    every redirect that already existed arrives at the same place.

    `dispatch` and not `get`, because the method does not matter: whatever is
    asked of this URL, the answer is the gateway.
    """

    def destination(self, request: HttpRequest) -> str:
        """Where the person was going. Checked before it is followed: `next` is
        written by whoever wrote the link, and an unchecked one forwards to
        any host that asks."""
        target = request.GET.get(REDIRECT_FIELD_NAME, "")
        return target if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}) else "/"

    def dispatch(self, request: HttpRequest) -> HttpResponse:
        if settings.ADMIN_PASSWORD_LOGIN:
            return admin.site.login(request)
        if request.user.is_authenticated:
            return redirect(self.destination(request))
        return redirect_to_login(self.destination(request), reverse("account_login"))


class CertificateView(LoginRequiredMixin, View):
    """`/certificado` - the door `docs/CERTIFICATE.md` promises.

    `Taxpayer.install_certificate` carried the full validation from the start
    and no shell ever called it: the admin excludes the fields and points at
    "the upload flow", which was this page, unwritten until 2026-09-19. The
    page carries the whole story - generate, request, upload - because the
    person arriving here holds a gap link, not the manual.

    Only an OWNER may install or replace: the visibility table gives that role
    alone `change` on the taxpayer, and the certificate is the most sensitive
    thing a taxpayer holds. `RoleBackend` is the one asker.
    """

    template_name = "ui/certificado.html"

    def state(self, request: HttpRequest, form: CertificateForm) -> HttpResponse:
        looking = cast(BaseUser, request.user)
        if looking.active_taxpayer_id is None:
            return redirect("home")
        if not looking.has_perm("data.change_taxpayer"):
            raise PermissionDenied("Sólo el titular puede instalar el certificado.")
        books = looking.active_taxpayer
        return render(request, self.template_name, {"form": form, "books": books})

    def get(self, request: HttpRequest) -> HttpResponse:
        return self.state(request, CertificateForm())

    def post(self, request: HttpRequest) -> HttpResponse:
        looking = cast(BaseUser, request.user)
        if looking.active_taxpayer_id is None:
            return redirect("home")
        if not looking.has_perm("data.change_taxpayer"):
            raise PermissionDenied("Sólo el titular puede instalar el certificado.")
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                access.install_certificate(
                    taxpayer=looking.active_taxpayer_id,
                    certificate=form.cleaned_data["certificate"].read(),
                    key=form.cleaned_data["key"].read(),
                )
                return redirect("home")
            except DomainRefusal as refusal:
                form.add_error("certificate", str(refusal))
        return self.state(request, form)
