# parley.models.base
# The abstract base model for all parley models.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Sat Oct 05 15:11:26 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: base.py [] benjamin@rotational.io $

"""
The abstract base model for all parley models.
"""

##########################################################################
## Imports
##########################################################################

import uuid

from django.db import models


##########################################################################
## Base Model
##########################################################################

class BaseModel(models.Model):
    """
    In order to make it easier to ingest data and audit records added to parlance, the
    base model uses UUIDs as the primary key instead of sequences and adds timestamps
    to track modifications to all objects in the system.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="The globally unique identifier of the object",
    )

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text="The timestamp that the object was created",
    )

    modified = models.DateTimeField(
        auto_now=True,
        editable=False,
        help_text="The timestamp that the object was last modified",
    )

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """
    Adds created and modified timestamps to sub-models.
    """

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text="The timestamp that the object was created",
    )

    modified = models.DateTimeField(
        auto_now=True,
        editable=False,
        help_text="The timestamp that the object was last modified",
    )

    class Meta:
        abstract = True
