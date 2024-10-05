# parley.models.user
# Implements models need to track user evaluations and reviews.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Sat Oct 05 16:41:47 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: user.py [] benjamin@rotational.io $

"""
Implements models need to track user evaluations and reviews.
"""

##########################################################################
## Imports
##########################################################################

from .base import TimestampedModel

from django.db import models


##########################################################################
## Models
##########################################################################

class ReviewTask(TimestampedModel):

    user = models.ForeignKey(
        'auth.User',
        null=False,
        on_delete=models.CASCADE,
        related_name="review_tasks",
        help_text="The user that is conducting the evaluation",
    )

    evaluation = models.ForeignKey(
        "parley.Evaluation",
        null=False,
        on_delete=models.CASCADE,
        related_name="review_tasks",
        help_text="The evaluation the user is performing",
    )

    responses = models.ManyToManyField(
        'parley.Response', through='parley.ResponseReview'
    )

    started_on = models.DateTimeField(
        null=True, default=None,
        help_text="The timestamp that the review was start on, null if not started"
    )

    completed_on = models.DateTimeField(
        null=True, default=None,
        help_text="The timestamp that the review was completed, null if not completed",
    )

    class Meta:
        db_table = "review_tasks"
        ordering = ("-created",)
        get_latest_by = "created"
        unique_together = ("user", "evaluation")

    @property
    def is_started(self):
        return self.started_on is not None

    @property
    def is_completed(self):
        return self.completed_on is not None


class ResponseReview(TimestampedModel):

    review = models.ForeignKey(
        "parley.ReviewTask",
        null=False,
        on_delete=models.CASCADE,
        related_name="response_reviews",
        help_text="The individual response reviews in a review",
    )

    response = models.ForeignKey(
        'parley.Response',
        null=False,
        on_delete=models.CASCADE,
        related_name=("reviews"),
    )

    output_correct = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text=(
            "Was the output correct based on the expected output or the prompt "
            "(or almost correct for fuzzy qualitative correctness)?"
        ),
    )

    label_correct = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text=(
            "Was the output label correct based on the expected label "
            "(or almost correct for fuzzy label matching)?"
        ),
    )

    is_confabulation = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text="Is the output a hallucination or confabulation?",
    )

    is_readable = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text="Does the output contain grammatically correct, understandable language?",
    )

    class Meta:
        db_table = "response_reviews"
        ordering = ("-created",)
        get_latest_by = "created"
        unique_together = ("review", "response")
