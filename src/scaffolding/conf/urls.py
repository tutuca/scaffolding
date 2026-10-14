from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from scaffolding.interface.api import urls
from scaffolding.interface.web.views import ColophonView, HomeView, NotesView

admin.site.site_header = "Scaffolding"
admin.site.site_title = "Scaffolding"

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Version captured, not hardcoded; URLPathVersioning validates it against ALLOWED_VERSIONS.
    re_path(r"^api/v(?P<version>[0-9]+\.[0-9]+)/", include(urls.urlpatterns)),
    path("login/", auth_views.LoginView.as_view(template_name="ui/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("notes/", NotesView.as_view(), name="notes"),
    path("colophon/", ColophonView.as_view(), name="colophon"),
    # The front page, shadowing the admin's index: `path("")` matches the empty
    # path exactly, so every other admin URL falls through to the catch-all.
    path("", HomeView.as_view(), name="home"),
    # Must stay last: AdminSite closes its URLconf with a catch-all.
    path("", admin.site.urls),
]
