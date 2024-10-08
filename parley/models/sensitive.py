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

import re

from django.db import models
from .base import TimestampedModel


class Sensitive(TimestampedModel):
    """
    Any data or information that should be considered sensitive and not included
    in any output across any evaluation. These can be specific strings or they can
    be regular expressions to search the output for.
    """

    term = models.CharField(
        blank=False,
        null=False,
        max_length=255,
        unique=True,
        help_text="The search term to look for sensitive data in output",
    )

    is_regex = models.BooleanField(
        null=False,
        default=False,
        help_text="If the term is a regular expression to analyze the output on",
    )

    is_name = models.BooleanField(
        null=False,
        default=False,
        help_text="If the term is a proper name that may be extracted and fuzzy searched with NER",
    )

    case_sensitive = models.BooleanField(
        null=False,
        default=False,
        help_text="Do not use case insensitive search to locate the sensitive term",
    )

    class Meta:
        db_table = "sensitive"
        ordering = ("-created",)
        get_latest_by = "created"
        verbose_name = "sensitive"
        verbose_name_plural = "sensitive"

    def search(self, text: str) -> bool:
        if self.is_regex:
            args = [self.term, text]
            if not self.case_sensitive:
                args.append(re.IGNORECASE)

            if re.search(*args):
                return True
            return False

        if not self.case_sensitive:
            text = text.casefold()
            term = self.term.casefold()
        else:
            term = self.term

        return text.find(term) > -1

    def __str__(self):
        return self.term
