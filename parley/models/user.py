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
from .enums import FivePointLikert

from django.db import models
from django.urls import reverse


##########################################################################
## Models
##########################################################################


class ReviewTask(TimestampedModel):

    user = models.ForeignKey(
        "auth.User",
        null=False,
        on_delete=models.CASCADE,
        related_name="review_tasks",
        help_text="The user that is conducting the evaluation",
    )

    model_evaluation = models.ForeignKey(
        "parley.ModelEvaluation",
        null=False,
        on_delete=models.CASCADE,
        related_name="review_tasks",
        help_text="The evaluation the user is performing",
    )

    responses = models.ManyToManyField(
        "parley.Response", through="parley.ResponseReview"
    )

    started_on = models.DateTimeField(
        null=True,
        default=None,
        blank=True,
        help_text="The timestamp that the review was start on, null if not started",
    )

    completed_on = models.DateTimeField(
        null=True,
        default=None,
        blank=True,
        help_text="The timestamp that the review was completed, null if not completed",
    )

    class Meta:
        db_table = "review_tasks"
        ordering = ("-created",)
        get_latest_by = "created"
        unique_together = ("user", "model_evaluation")

    @property
    def evaluation(self):
        return self.model_evaluation.evaluation

    @property
    def model(self):
        return self.model_evaluation.model

    def prompts(self):
        return self.model_evaluation.prompts()

    @property
    def is_started(self):
        return self.started_on is not None

    @property
    def is_completed(self):
        return self.completed_on is not None

    @property
    def percent_complete(self):
        n_prompts = self.prompts().count()
        if n_prompts == 0:
            return 0
        n_reviews = self.response_reviews.count()
        return int((float(n_reviews) / float(n_prompts)) * 100)

    def __str__(self):
        return f"{self.evaluation.name} ({self.model.name})"

    def get_absolute_url(self):
        return reverse("review-task", args=(self.id,))


class ResponseReview(TimestampedModel):

    review = models.ForeignKey(
        "parley.ReviewTask",
        null=False,
        on_delete=models.CASCADE,
        related_name="response_reviews",
        help_text="The individual response reviews in a review",
    )

    response = models.ForeignKey(
        "parley.Response",
        null=False,
        on_delete=models.CASCADE,
        related_name="reviews",
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

    is_factual = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text="Is the output factually correct?",
    )

    is_readable = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text="Does the output contain grammatically correct, understandable language?",
    )

    is_correct_style = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text="Is the output written in the correct style or tone?",
    )

    helpfulness = models.IntegerField(
        choices=FivePointLikert.choices,
        null=True,
        default=None,
        blank=True,
        help_text="This output is helpful to the reader",
    )

    notes = models.TextField(
        null=True,
        default=None,
        blank=True,
        help_text="Any notes the reviewer would like to add about the output",
    )

    class Meta:
        db_table = "response_reviews"
        ordering = ("-created",)
        get_latest_by = "created"
        unique_together = ("review", "response")
