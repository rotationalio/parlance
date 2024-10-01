# parlance
# The primary entry point for the parlance web app.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 14:56:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: __init__.py [] benjamin@rotational.io $

"""
The primary entry point for the parlance web app.
"""

##########################################################################
## Imports
##########################################################################

from .version import get_version, get_revision, __version_info__

__version__ = get_version()
