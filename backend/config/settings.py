import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
if not ENV_FILE.is_file():
    raise ImproperlyConfigured(f"Required environment file not found: {ENV_FILE}")
load_dotenv(ENV_FILE)


def required_env(name):
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise ImproperlyConfigured(f"{name} must be set in {ENV_FILE}")
    return value.strip()


def required_bool(name):
    value = required_env(name).lower()
    if value not in {"true", "false"}:
        raise ImproperlyConfigured(f"{name} must be True or False")
    return value == "true"


def optional_env_list(name):
    value = os.environ.get(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


DEBUG = required_bool("DEBUG")
SECRET_KEY = required_env("SECRET_KEY")
ALLOWED_HOSTS = [host.strip() for host in required_env("ALLOWED_HOSTS").split(",")]
CSRF_TRUSTED_ORIGINS = optional_env_list("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "common",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "accounts",
    "cards",
    "transactions",
    "merchants",
    "notifications",
    "savings",
    "charity",
    "recharge",
    "billpay",
    "agents",
    "banking",
    "loans",
    "remittance",
    "rewards",
    "gateway",
    "tickets",
    "support",
    "statements",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "common.middleware.RequestLoggingMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": required_env("DB_NAME"),
        "USER": required_env("DB_USER"),
        "PASSWORD": required_env("DB_PASSWORD"),
        "HOST": required_env("DB_HOST"),
        "PORT": required_env("DB_PORT"),
        "CONN_MAX_AGE": int(required_env("DB_CONN_MAX_AGE")),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_ROOT.mkdir(exist_ok=True)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True
if not DEBUG:
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in required_env("CORS_ALLOWED_ORIGINS").split(",")
        if origin.strip()
    ]
    SECURE_SSL_REDIRECT = required_bool("SECURE_SSL_REDIRECT")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(required_env("SECURE_HSTS_SECONDS"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = required_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS")
    SECURE_HSTS_PRELOAD = required_bool("SECURE_HSTS_PRELOAD")
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(required_env("ACCESS_TOKEN_MINUTES"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=int(required_env("REFRESH_TOKEN_MINUTES"))),
}

TRANSFER_FEE_PERCENT = float(required_env("TRANSFER_FEE_PERCENT"))
PAGE_SIZE = int(required_env("PAGE_SIZE"))
PAGE_SIZE_MAX = int(required_env("PAGE_SIZE_MAX"))

LOGGING_DIR = BASE_DIR / "logs"
LOGGING_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {module}:{lineno} {message}",
            "style": "{",
        },
        "request": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_DIR / "error.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "level": "ERROR",
        },
        "file_request": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_DIR / "request.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "request",
        },
    },
    "loggers": {
        "common": {
            "handlers": ["file_error"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "common.middleware": {
            "handlers": ["file_request", "file_error"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["file_error"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "cards": {
            "handlers": ["file_error"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "transactions": {
            "handlers": ["file_error"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "merchants": {
            "handlers": ["file_error"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "notifications": {
            "handlers": ["file_error"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file_error"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
