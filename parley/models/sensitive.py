# parley.models.sensitive
# Handling of sensitive data and validation.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Sat Oct 05 15:11:26 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: llm.py [] benjamin@rotational.io $

"""
Handling of sensitive data and validation.
"""

##########################################################################
## Imports
##########################################################################

from .base import BaseModel
from django.db import models


class Sensitive(BaseModel):
    """
    Any data or information that should be considered sensitive and not included
    in any output across any evaluation. These can be specific strings or they can
    be regular expressions to search the output for.
    """

    term = models.CharField(
        blank=False,
        null=False,
        max_length=255,
        help_text="The search term to look for sensitive data in output",
    )

    is_regex = models.BooleanField(
        null=False,
        default=False,
        help_text="If the term is a regular expression to analyze the output on",
    )

    class Meta:
        db_table = "sensitive"
        ordering = ("-created",)
        get_latest_by = "created"
        verbose_name = "sensitive"
        verbose_name_plural = "sensitive"
