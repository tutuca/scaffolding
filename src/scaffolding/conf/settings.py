"""
Settings. Single file, environment-driven via django-environ.

Secrets policy: nothing sensitive lives in the repo. Every secret or
machine-specific value comes from the environment (or `.env`, gitignored).
See `.env.example` and `docs/ARCHITECTURE.md` for the sensitivity matrix.

Single machine, single superuser, SQLite. Not designed to be deployed.
"""

from pathlib import Path

import environ  # type: ignore[import-untyped]

from scaffolding.conf.oauth import client_credentials
from scaffolding.interface.adapter.google.scopes import SCOPES as GOOGLE_SCOPES

# src/scaffolding/conf/settings.py -> project root. The defaults below follow the
# checkout's layout; an installed wheel overrides them with SCAFFOLDING_VAR_DIR /
# SCAFFOLDING_SECRETS_DIR - its state cannot live inside site-packages, where an
# upgrade would wipe it.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

env = environ.Env()
env.read_env(str(PROJECT_ROOT / ".env"))

VAR_DIR = Path(env("SCAFFOLDING_VAR_DIR", default=str(PROJECT_ROOT / "var")))
# The certificate and private key, mode 0600. Gitignored.
SECRETS_DIR = Path(env("SCAFFOLDING_SECRETS_DIR", default=str(PROJECT_ROOT / "etc" / "secrets")))

# Local-only tool; the default keeps mypy/pytest working on a fresh clone. Set a real
# one in .env before trusting sessions. `conf/serving.py` refuses to serve on this
# value unless DEBUG is on, and `data/checks.py` names it under `check --deploy`.
INSECURE_SECRET_KEY = "insecure-dev-key-set-me-in-.env"
SECRET_KEY = env("SECRET_KEY", default=INSECURE_SECRET_KEY)
DEBUG = env.bool("DEBUG", default=False)
# `localhost` alone, never `127.0.0.1`: same server, two origins to Google, and allauth mirrors
# the request's host into `redirect_uri`. Only one of them is a registered callback.
ALLOWED_HOSTS = ["localhost"]

INSTALLED_APPS = [
    # First, and only for template resolution: `APP_DIRS` searches in this order
    # and takes the first match, so `admin/base_site.html` and
    # `allauth/layouts/base.html` under `ui` must come before the apps that ship
    # them. It has no models, so nothing else depends on the position.
    "scaffolding.ui.apps.UiConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # allauth needs a Site; there is one, and it is this installation.
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "rest_framework",
    "drf_spectacular",
    "django_tasks_db",
    "scaffolding.data",
    "scaffolding.interface.cli",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # The notebook pages are 140 KB of HTML and JSON read models; 92 KiB of that
    # is what Lighthouse measured as saved by compression (2026-10-08). BREACH is
    # answered by Django masking the CSRF token on every response.
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
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

# The SQLite file is itself sensitive data: gitignored, keep it on an encrypted volume.
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{VAR_DIR / 'database.sqlite'}"),
    # The task queue: its own SQLite, so a worker's rows never touch or bloat the
    # ledger. Not books, but it holds them - task kwargs and results carry
    # transcripts until `prune_tasks` clears them weekly. Routed by `conf/router.py`.
    "tasks": env.db("TASKS_DATABASE_URL", default=f"sqlite:///{VAR_DIR / 'tasks.sqlite'}"),
}
# Which database each model's rows live on: the task queue to `tasks`, the rest to
# `default` (see `conf/router.py`).
DATABASE_ROUTERS = ["scaffolding.conf.router.TaskRouter"]
# Where `scaffolding valuation --write` leaves its report. The journal itself is a
# table now (`data.ReversalEntry`); this is only the rendered artifact, which is
# ledger data all the same - gitignored and 0600 like the database beside it.
VALUATION_REPORT = env("VALUATION_REPORT", default=str(VAR_DIR / "valuation.md"))

# The bills - rent coupons, electricity and gas liquidations - `movements bills` reads.
BILLS_FOLDER = env("BILLS_FOLDER", default=str(VAR_DIR / "documents" / "expenses"))

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

# Ours from the first migration, never django.contrib.auth.User. Swapping
# AUTH_USER_MODEL after a table has rows in it is the expensive mistake this
# avoids: every owner column added first makes it costlier.
AUTH_USER_MODEL = "data.BaseUser"

# ModelBackend answers from `user_permissions` and `groups` and handles the
# password login; allauth handles the Google one. RoleBackend answers the
# question that matters here - what this person's role on the books they are
# looking at allows - and is the only reader of `data/visibility.py`.
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "scaffolding.data.backends.RoleBackend",
]

# Fernet key encrypting uploaded ARCA private keys at rest. Generate one with
# `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
SECRETS_ENCRYPTION_KEY = env("SECRETS_ENCRYPTION_KEY", default="")

# Read by one thing: the test that refuses to let a CUIT be committed. It used
# to read TAXPAYER_CUIT, which was the taxpayer's own CUIT in settings; that
# moved onto the Taxpayer row, where a test database cannot see it. The guard
# still needs to know what to look for, so it gets its own name, and nothing
# else in the app reads it.
REDACTED_CUIT = env("REDACTED_CUIT", default="")

SITE_ID = 1

# ---------------------------------------------------------------------------
# The gateway. Google is the only door: `SOCIALACCOUNT_ONLY` removes allauth's
# local login and signup views entirely, so there is nothing else to guard.
#
# ModelBackend stays above, deliberately. A local tool needs a way into the
# admin when the OAuth client is misconfigured, and the suite needs users
# without an OAuth round trip. It opens nothing for a regular account, which has
# no usable password to use.
# ---------------------------------------------------------------------------
SOCIALACCOUNT_ONLY = True
# Google verified the address already. Verifying it again would need an email
# backend this tool does not have.
ACCOUNT_EMAIL_VERIFICATION = "none"
# There is no username to log in with or to generate: `BaseUser` has an email
# and nothing else. Saying so stops allauth and dj-rest-auth building forms
# around a field that does not exist.
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*"]
SOCIALACCOUNT_ADAPTER = "scaffolding.service.gateway.GatewayAdapter"
# The home page, which says what is missing and offers the way onward. It
# shadows the admin index at "/" deliberately; see `conf/urls.py`.
LOGIN_REDIRECT_URL = "/"
# allauth defaults this to False, and then the consent Google grants is thrown
# away the moment it arrives: login still works, and `scaffolding archive` has no
# credentials to call Drive with. The whole point of asking for the scopes is to
# keep what comes back.
SOCIALACCOUNT_STORE_TOKENS = True

# The admin's own password form at /login/, off by default: a second door that
# `ModelBackend` answers is still a second door, and `interface/web` claims the
# path to forward it to Google. Turning this on is the escape hatch the backend
# list above exists for - an OAuth client that will not load, and a superuser who
# has to get in and fix it.
ADMIN_PASSWORD_LOGIN = env.bool("ADMIN_PASSWORD_LOGIN", default=False)

# Who may register at all. allauth's default is any Google account, which is the
# wrong default for a ledger - and an empty list here means nobody, not everybody.
SIGNUP_ALLOWED_EMAILS = env.list("SIGNUP_ALLOWED_EMAILS", default=[])

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # From the file Google hands you, not a SocialApp row: the secrets
        # policy says nothing sensitive lives in the repo, and a row is a thing
        # to seed, back up and keep out of fixtures.
        "APP": client_credentials(env("GOOGLE_OAUTH_WEB_CLIENT", default=str(SECRETS_DIR / "google-client-web.json"))),
        "SCOPE": ["openid", "email", "profile", *GOOGLE_SCOPES],
        # `access_type=offline` with `consent`, not either alone: offline by
        # itself returns a refresh token on the first consent and never again,
        # so a re-login would leave an access token that expires in an hour.
        #
        # `select_account` because the account decides whose Drive the archive
        # lands in. Without it Google takes whichever session the browser
        # happens to hold, which on a machine signed into work is the wrong one
        # and says so only as an org policy error.
        "AUTH_PARAMS": {"access_type": "offline", "prompt": "select_account consent"},
    }
}

# The Desktop OAuth client `scaffolding login` runs its loopback consent against,
# as the JSON Google hands you when you create it. A path rather than two pasted
# values: retyping a client id is a step that can go wrong silently, and the file
# is already the shape `InstalledAppFlow` reads.
#
# A second registration, not a second token store: both paths end at the same
# SocialToken row with the same scopes.
GOOGLE_OAUTH_DESKTOP_CLIENT = env(
    "GOOGLE_OAUTH_DESKTOP_CLIENT", default=str(SECRETS_DIR / "google-client-secret-cli.json")
)

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Cordoba"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
# Where `collectstatic` writes. `runserver` with DEBUG serves straight from
# each app's directory and never reads this; a DEBUG=False run serves nothing
# at all, which is the `infrastructure` track's open question. Under `var/`
# because it is generated, not authored.
STATIC_ROOT = str(VAR_DIR / "static")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# API. The version segment is captured in the URL and validated against
# ALLOWED_VERSIONS; adding v1.1 later is a settings change, not a URL rewrite.
# ---------------------------------------------------------------------------
API_VERSION = "1.0"

REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": API_VERSION,
    "ALLOWED_VERSIONS": [API_VERSION],
    # One way in. The admin is this tool's primary UI and the browsable API
    # depends on the session; `scaffolding login` caches identity on disk rather
    # than over HTTP. Ours rather than DRF's, for the 401 challenge header.
    "DEFAULT_AUTHENTICATION_CLASSES": ["scaffolding.service.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "scaffolding",
    "DESCRIPTION": "Exportación de servicios · Factura E · Monotributo",
    "VERSION": f"{API_VERSION}.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # Fields sharing a choice set across components need naming once, or the
    # generator names the component after whichever field it reached first.
    # Currency: seven fields under three names (currency, fee_currency,
    # credited_currency). Institution: `source` on Movement and on both proxies
    # that read it, plus `Settlement.rail`.
    "ENUM_NAME_OVERRIDES": {
        "CurrencyEnum": "scaffolding.data.enums.Currency.choices",
        "InstitutionEnum": "scaffolding.data.enums.Institution.choices",
        "MovementKindEnum": "scaffolding.data.enums.MovementKind.choices",
    },
}


# ---------------------------------------------------------------------------
# ARCA. The certificate and private key are the most sensitive material in the
# system: whoever holds them can issue fiscal documents in your name. Paths
# only; the files live under etc/secrets/ (gitignored), mode 0600.
# ---------------------------------------------------------------------------
ARCA = {
    "ENV": env("ARCA_ENV", default="homologacion"),  # homologacion | produccion
    # dry_run / manual never touch the network. Default, so a fresh clone is safe to poke at.
    "AUTHORIZER": env("ARCA_AUTHORIZER", default="manual"),  # manual | dry_run | wsfex
    "RATE_PROVIDER": env("ARCA_RATE_PROVIDER", default="manual"),  # manual
}

# ---------------------------------------------------------------------------
# Background tasks. `interface/tasks` is the shell: thin `@task` functions over
# the same domain entry points the CLI calls. The database backend
# (`django-tasks-db`) stores enqueued tasks on the `tasks` database (routed by
# `conf/router.py`), and `scaffolding db_worker` runs them. Task arguments and return
# values round-trip through JSON - dates, decimals and enums cross the boundary
# as strings.
# ---------------------------------------------------------------------------
TASKS = {
    "default": {
        "BACKEND": "django_tasks_db.DatabaseBackend",
    },
}
