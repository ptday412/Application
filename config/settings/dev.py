from .base import *

SECRET_KEY = env('DEV_SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DEV_DB_NAME"),
        "USER": env("DEV_DB_USER"),
        "PASSWORD": env("DEV_DB_PASSWORD"),
        "HOST": env("DEV_DB_HOST"),
        "PORT": env("DEV_DB_PORT"),
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


CORS_ORIGIN_ALLOW_ALL = True