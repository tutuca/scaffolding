from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from scaffolding.interface.api import urls
from scaffolding.interface.web.investments import InvestmentsView
from scaffolding.interface.web.movimientos import MovimientosView, NamingView
from scaffolding.interface.web.planes import CompleteView, DropView, GoalsView, OrderView, PlansView, RestoreView
from scaffolding.interface.web.views import AdminLoginView, CertificateView, ColophonView, HomeView

admin.site.site_header = "Scaffolding"
admin.site.site_title = "Scaffolding"

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    # The gateway. Before the admin, which closes its URLconf with a catch-all.
    path("accounts/", include("allauth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Version captured, not hardcoded; URLPathVersioning validates it against ALLOWED_VERSIONS.
    re_path(r"^api/v(?P<version>[0-9]+\.[0-9]+)/", include(urls.urlpatterns)),
    # One door. The admin keeps a password form at /login/, and every redirect
    # for an anonymous visitor points at it - so the path is claimed here,
    # before the admin does, and forwards to the gateway above.
    path("login/", AdminLoginView.as_view()),
    # The books, before the admin's catch-all.
    path("notebooks/movimientos", MovimientosView.as_view(), name="movimientos"),
    path("notebooks/movimientos/nombrar/", NamingView.as_view(), name="nombrar"),
    path("notebooks/inversiones", InvestmentsView.as_view(), name="inversiones"),
    path("notebooks/planes", PlansView.as_view(), name="planes"),
    path("notebooks/planes/metas/", GoalsView.as_view(), name="metas"),
    path("notebooks/planes/metas/orden/", OrderView.as_view(), name="orden"),
    path("notebooks/planes/metas/<int:goal>/", GoalsView.as_view(), name="meta"),
    path("notebooks/planes/metas/<int:goal>/quitar/", DropView.as_view(), name="quitar"),
    path("notebooks/planes/metas/<int:goal>/cumplir/", CompleteView.as_view(), name="cumplir"),
    path("notebooks/planes/metas/<int:goal>/restaurar/", RestoreView.as_view(), name="restaurar"),
    path("certificado", CertificateView.as_view(), name="certificado"),
    path("colophon/", ColophonView.as_view(), name="colophon"),
    # The front page, and the one thing that may shadow the admin: `path("")`
    # matches the empty path exactly, so every other admin URL falls through to
    # the catch-all below. `reverse("admin:index")` still yields "/", which is
    # why this page carries the app list - the admin's breadcrumb lands here.
    path("", HomeView.as_view(), name="home"),
    # Must stay last: AdminSite closes its URLconf with a `(?P<url>.*)$` catch-all.
    path("", admin.site.urls),
]
