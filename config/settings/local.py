from .base import *

SECRET_KEY = env('LOCAL_SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

BASE_URL = 'http://127.0.0.1:8000/'

CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000/']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

LOGGING = {
    "version": 1,  # the dictConfig format version
    "disable_existing_loggers": False,  # retain the default loggers
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, 'logs', 'debug.log'),
            "level": "DEBUG",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["file"],
        },
        "diaries.views": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "formatters": {
        "verbose": {
            "format": "{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
}