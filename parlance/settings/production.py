# parlance.settings.production
# Configuration for the production environment.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 14:56:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: base.py [] benjamin@rotational.io $

"""
Configuration for the production environment.
"""

##########################################################################
## Imports
##########################################################################

import sentry_sdk

from .base import *  # noqa
from .base import PROJECT, environ_setting

from ..version import get_sentry_release
from sentry_sdk.integrations.django import DjangoIntegration


##########################################################################
## Production Environment
##########################################################################

## Ensure debug mode is not running production
DEBUG = False

## Hosts
ALLOWED_HOSTS = [
    "parlance.rotational.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://parlance.rotational.app",
]

## SSL is terminated at Traefik so all requests will be http in the k8s cluster.
SECURE_SSL_REDIRECT = False

## Ensure that the Traefik proxy causes Django to act like its behind TLS
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

## Static files served by WhiteNoise
STATIC_ROOT = PROJECT / "assets"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


##########################################################################
## Sentry Error Management
##########################################################################

sentry_sdk.init(
    dsn=environ_setting("SENTRY_DSN"),
    integrations=[DjangoIntegration()],

    # Get release from Heroku environment or specify develop release
    release=get_sentry_release(),
    environment="production",

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,

    # Set a uniform sample rate
    traces_sample_rate=0.5,
)
