"""Settings. Single file, environment-driven via django-environ.

Secrets policy: nothing sensitive lives in the repo. Every secret or
machine-specific value comes from the environment (or `.env`, gitignored).
See `.env.example` and `docs/ARCHITECTURE.md`.
"""

from pathlib import Path

import environ  # type: ignore[import-untyped]

# src/scaffolding/conf/settings.py -> project root. The defaults below follow the
# checkout's layout; an installed wheel overrides them with SCAFFOLDING_VAR_DIR /
# SCAFFOLDING_SECRETS_DIR - its state cannot live inside site-packages, where an
# upgrade would wipe it.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

env = environ.Env()
env.read_env(str(PROJECT_ROOT / ".env"))

VAR_DIR = Path(env("SCAFFOLDING_VAR_DIR", default=str(PROJECT_ROOT / "var")))
SECRETS_DIR = Path(env("SCAFFOLDING_SECRETS_DIR", default=str(PROJECT_ROOT / "etc" / "secrets")))

# Local tool; the default keeps mypy/pytest working on a fresh clone. Set a real
# one in .env before trusting sessions. `conf/serving.py` refuses to serve on this
# value unless DEBUG is on, and `data/checks.py` names it under `check --deploy`.
INSECURE_SECRET_KEY = "insecure-dev-key-set-me-in-.env"
SECRET_KEY = env("SECRET_KEY", default=INSECURE_SECRET_KEY)
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = ["localhost"]

INSTALLED_APPS = [
    # First, and only for template resolution: `APP_DIRS` searches in this order
    # and takes the first match, so `admin/base_site.html` under `ui` must come
    # before the apps that ship it. It has no models.
    "scaffolding.ui.apps.UiConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "django_tasks_db",
    "scaffolding.data",
    "scaffolding.interface.cli",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "scaffolding.conf.urls"
WSGI_APPLICATION = "scaffolding.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{VAR_DIR / 'database.sqlite'}"),
    # The task queue: its own SQLite, so worker rows never touch or bloat the app
    # database. Routed by `conf/router.py`.
    "tasks": env.db("TASKS_DATABASE_URL", default=f"sqlite:///{VAR_DIR / 'tasks.sqlite'}"),
}
DATABASE_ROUTERS = ["scaffolding.conf.router.TaskRouter"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

# Ours from the first migration, never django.contrib.auth.User.
AUTH_USER_MODEL = "data.BaseUser"

# ModelBackend answers from `user_permissions`/`groups`; RoleBackend answers what
# a role allows on the tenant being looked at (data/visibility.py).
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "scaffolding.data.backends.RoleBackend",
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
# Where `collectstatic` writes. Under `var/` because it is generated, not authored.
STATIC_ROOT = str(VAR_DIR / "static")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# The version segment, captured in the URL and validated against ALLOWED_VERSIONS.
API_VERSION = "1.0"

REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": API_VERSION,
    "ALLOWED_VERSIONS": [API_VERSION],
    "DEFAULT_AUTHENTICATION_CLASSES": ["scaffolding.service.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "scaffolding",
    "DESCRIPTION": "A multi-tenant Django application scaffold.",
    "VERSION": f"{API_VERSION}.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Background tasks. `interface/tasks` is the shell: thin `@task` functions over
# the same domain entry points the CLI calls. `django-tasks-db` stores enqueued
# tasks on the `tasks` database (routed by `conf/router.py`).
TASKS = {
    "default": {
        "BACKEND": "django_tasks_db.DatabaseBackend",
    },
}
