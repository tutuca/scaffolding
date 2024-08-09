"""scaffolding URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Samples
    2. Add a URL to urlpatterns:  url(r'^$', Samples.as_view(), name='home')
Including another URLconf
    1. Add an import:  from samples import urls as samples_urls
    2. Add a URL to urlpatterns:  url(r'^samples/', include(samples_urls))
"""

from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView

from .router import router


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("about", TemplateView.as_view(template_name="about.html"), name="about"),
    path("sandbox", TemplateView.as_view(template_name="sandbox.html"), name="sandbox"),
    path("api/", include(router.urls)),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
