#!/usr/bin/env python
# manage.py
# Django management script and admin commands.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 14:56:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: manage.py [] benjamin@rotational.io $

"""
Django's command-line utility for administrative tasks.
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import dotenv


try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc


def main():
    """
    Run administrative tasks.
    """
    dotenv.load_dotenv(dotenv.find_dotenv())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parlance.settings.development')
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
