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


##########################################################################
## Container Environment
##########################################################################

## Ensure debug mode is not running production
DEBUG = False

## Hosts
ALLOWED_HOSTS = [
    "parlance.rotational.dev",
]

## Static files served by WhiteNoise
STATIC_ROOT = PROJECT / "assets"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
