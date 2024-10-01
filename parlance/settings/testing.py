# parlance.settings.testing
# Configuration for the testing environment.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 14:56:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: base.py [] benjamin@rotational.io $

"""
Configuration for the testing environment.
"""

##########################################################################
## Imports
##########################################################################

from .base import *  # noqa
from .base import REST_FRAMEWORK


##########################################################################
## Test Settings
##########################################################################

## Hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

## Content without side effects
MEDIA_ROOT = "/tmp/ledger_test/media"
STATIC_ROOT = "/tmp/ledger_test/static"


##########################################################################
## Django REST Framework
##########################################################################

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework.authentication.BasicAuthentication",
)
