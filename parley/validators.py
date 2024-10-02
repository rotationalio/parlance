# parley.validators
# Field validation helpers for the parley app.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 18:28:16 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: validators.py [] benjamin@rotational.io $

"""
Field validation helpers for the parley app.
"""

##########################################################################
## Imports
##########################################################################

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


##########################################################################
## VALIDATION
##########################################################################

SEMVER_REGEXP = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")  # noqa


def validate_semver(value):
    if not SEMVER_REGEXP.match(value):
        raise ValidationError(
            _("%(value)s is not a valid semantic version"),
            params={"value": value},
        )
