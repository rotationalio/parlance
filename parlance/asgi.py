# parlance.asgi
# ASGI config for parlance project.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 14:56:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: asgi.py [] benjamin@rotational.io $

"""
ASGI config for parlance project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

##########################################################################
## Imports
##########################################################################

import os
import dotenv

from django.core.asgi import get_asgi_application


##########################################################################
## WSGI Configuration
##########################################################################

# load .env file
dotenv.load_dotenv(dotenv.find_dotenv())

# set default environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parlance.settings.development")

application = get_asgi_application()
