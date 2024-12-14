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

# STORAGES = {
#     "default": {
#         "BACKEND": "storages.backends.s3.S3Storage",
#         "OPTIONS": {
            
#         },
#     },
# }


CORS_ORIGIN_ALLOW_ALL = True