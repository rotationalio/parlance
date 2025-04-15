# parlance.settings.development
# Configuration for the development environment.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 14:56:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: base.py [] benjamin@rotational.io $

"""
Configuration for the development environment.
"""

##########################################################################
## Imports
##########################################################################

import sentry_sdk

from .base import *  # noqa
from .base import PROJECT, environ_setting
from .base import INSTALLED_APPS, MIDDLEWARE

from ..version import get_sentry_release
from sentry_sdk.integrations.django import DjangoIntegration


##########################################################################
## Development Environment
##########################################################################

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

MEDIA_ROOT = PROJECT / "tmp" / "uploads"

## Static files served by WhiteNoise nostatic server
STATIC_ROOT = PROJECT / "tmp" / "static"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Debugging email without SMTP
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = PROJECT / "tmp" / "outbox"

# Debugging tools
INSTALLED_APPS += [
    "django_browser_reload",
]

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

##########################################################################
## Sentry Error Management
##########################################################################

sentry_sdk.init(
    dsn=environ_setting("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    # Get release from Heroku environment or specify develop release
    release=get_sentry_release(),
    environment="development",
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    # Set a uniform sample rate
    traces_sample_rate=1.0,
)
