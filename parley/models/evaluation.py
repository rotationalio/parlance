# parley.models.evaluation
# Evaluations and the prompts associated with those evaluations.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Sat Oct 05 15:11:26 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: evaluation.py [] benjamin@rotational.io $

"""
The abstract base model for all parley models.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models

from .base import BaseModel
from .enums import SimilarityMetric, OutputFormat


class Evaluation(BaseModel):
    """
    An Evaluation is a collection of related prompts that are used to perform a
    qualitative LLM evaluation. All of the prompts in the evaluation should be handled
    together, both when creating prompt outputs for a specific model and performing
    qualitative model evaluations.
    """

    name = models.CharField(
        default=None,
        null=False,
        blank=False,
        max_length=255,
        help_text="The descriptive name of the evaluation prompts collection",
    )

    task = models.CharField(
        default=None,
        null=False,
        blank=False,
        max_length=255,
        help_text="A description of the expected task or agent being evaluated",
    )

    description = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text="Any notes or other descriptive information about the evaluation",
    )

    similarity_metric = models.CharField(
        null=False,
        max_length=4,
        choices=SimilarityMetric,
        default=SimilarityMetric.COSINE_TFIDF,
        help_text="The similarity metric used to compare output to expected output",
    )

    similarity_threshold = models.FloatField(
        default=0.5,
        help_text="The similarity threshold to determine if an output is generally correct or not",
    )

    active = models.BooleanField(
        default=True,
        null=False,
        help_text="This prompt set should be used in evaluations of new models",
    )

    llms = models.ManyToManyField(
        "parley.LLM",
        through="parley.ModelEvaluation",
    )

    reviewers = models.ManyToManyField(
        "auth.User",
        through="parley.ReviewTask",
    )

    class Meta:
        db_table = "evaluations"
        ordering = ("-created",)
        get_latest_by = "created"
        verbose_name = "evaluation"
        verbose_name_plural = "evaluations"

    def __str__(self):
        return self.name


class Prompt(BaseModel):
    """
    A prompt is a single instance of an input to an LLM.
    """

    system = models.TextField(
        null=True,
        default=None,
        blank=True,
        help_text="The system prompt specified to the LLM",
    )

    prompt = models.TextField(
        null=False,
        default=None,
        blank=False,
        help_text="The prompt used to generate an output from an LLM",
    )

    evaluation = models.ForeignKey(
        "parley.Evaluation",
        null=False,
        on_delete=models.CASCADE,
        related_name="prompts",
        help_text="The evaluation that this prompt is a part of",
    )

    history = models.JSONField(
        null=True,
        default=None,
        blank=True,
        help_text="An array of prompt IDs that precede this prompt during evaluation",
    )

    notes = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text="Any notes or other descriptive information about the prompt",
    )

    expected_output_type = models.CharField(
        max_length=4,
        choices=OutputFormat,
        default=OutputFormat.TEXT,
        help_text="Specify the expected type of output for the prompt to validate",
    )

    expected_output = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text="Expected output for the prompt to use similarity scoring with",
    )

    expected_label = models.CharField(
        null=True,
        blank=True,
        default=None,
        max_length=255,
        help_text="For classifiers, expected label that should be contained in output",
    )

    order = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        help_text="Manually specify the order of the prompts for review",
    )

    exclude = models.BooleanField(
        default=False,
        help_text="Exclude this prompt from evaluations and from metrics",
    )

    class Meta:
        db_table = "prompts"
        ordering = ("order", "-created")
        get_latest_by = "created"
        verbose_name = "prompt"
        verbose_name_plural = "prompts"
