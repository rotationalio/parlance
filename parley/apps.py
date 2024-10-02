# parley.apps
# Parley app configuration.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 17:59:43 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: apps.py [] benjamin@rotational.io $

"""
Parley app configuration.
"""

##########################################################################
## Imports
##########################################################################

from django.apps import AppConfig


##########################################################################
## Parley Application Configuration
##########################################################################

class ParleyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "parley"
