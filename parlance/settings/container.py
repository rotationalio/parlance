# parlance.settings.container
# Configuration for the container environment.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 14:56:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: base.py [] benjamin@rotational.io $

"""
Configuration for the container environment.
"""

##########################################################################
## Imports
##########################################################################

from .base import *  # noqa
from .base import PROJECT
from .base import environ_setting


##########################################################################
## Container Environment
##########################################################################

## Ensure debug mode is not running production
DEBUG = False

## Hosts
ALLOWED_HOSTS = [
    "parlance.rotational.app",
]

## Static files served by WhiteNoise
STATIC_ROOT = environ_setting("STATIC_ROOT", default=PROJECT / "storage" / "static")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

## Media files and uploads
MEDIA_ROOT = environ_setting("MEDIA_ROOT", default=PROJECT / "storage" / "uploads")
