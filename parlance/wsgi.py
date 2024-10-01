# parlance.wsgi
# WSGI config for parlance project.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 14:56:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: wsgi.py [] benjamin@rotational.io $

"""
WSGI config for parlance project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

##########################################################################
## Imports
##########################################################################

import os
import dotenv

from django.core.wsgi import get_wsgi_application


##########################################################################
## WSGI Configuration
##########################################################################

# load .env file
dotenv.load_dotenv(dotenv.find_dotenv())

# set default environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parlance.settings.development")

# export the wsgi application for import
application = get_wsgi_application()
