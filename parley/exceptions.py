# parley.exceptions
# Parley application exceptions
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Thu Oct 03 12:21:54 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: exceptions.py [] benjamin@rotational.io $

"""
Parley application exceptions
"""


##########################################################################
## Exceptions
##########################################################################

class ParlanceError(Exception):
    """
    Base class for parlance errors
    """


class ParlanceUploadError(ParlanceError):
    """
    Trouble uploading a file to import data into parlance
    """
