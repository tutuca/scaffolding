import environ
from pathlib import Path


env = environ.Env()
environ.Env.read_env()  # reading .env file
BASE_DIR = Path(__file__).parent

PROJECT_NAME = "scaffolding"
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "KmUtzuywYdlTFjlwGCfIvI2BSYq2gzLEx+iIzRluhafgSsK5h3%"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Application definition

BASE_APPS = (
    "allauth.account",
    "allauth.socialaccount",
    "allauth.usersessions",
    "allauth",
    "corsheaders",
    "debug_toolbar",
    "dj_rest_auth.registration",
    "dj_rest_auth",
    "django_extensions",
    "django_filters",
    "django_vite",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
)

PROJECT_APPS = ("common", "samples", "users")

INSTALLED_APPS = BASE_APPS + PROJECT_APPS

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "allauth.usersessions.middleware.UserSessionsMiddleware",
]

ROOT_URLCONF = "scaffolding.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates", BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

WSGI_APPLICATION = "scaffolding.wsgi.application"

CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (
#     'localhost:*',
# )

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    "default": env.db("DB_URL", default="sqlite:///data/db.sqlite3"),
}

# DATABASE_ROUTERS = ["legacy.routers.scaffoldingRouter"]

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = env.str("LANGUAGE_CODE", default="es-ar")
TIME_ZONE = env.str("TIME_ZONE", default="America/Argentina/Cordoba")
USE_I18N = env.bool("USE_I18N", default=True)
USE_L10N = env.bool("USE_L10N", default=True)
USE_TZ = env.bool("USE_TZ", default=True)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/


MEDIA_ROOT = env.path("MEDIA_ROOT", "media")
MEDIA_URL = "/media/"

STATIC_ROOT = env.path("STATIC_ROOT", "static")
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_port": env.int("DJANGO_VITE_DEV_SERVER_PORT", default=5173),
    }
}

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "PAGE_SIZE": 12,
}

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": env.str("GOOGLE_API_CLIENT_ID", default=""),
            "secret": env.str("GOOGLE_API_SECRET", default=""),
            "key": env.str("GOOGLE_API_KEY", default=""),
        }
    }
}
