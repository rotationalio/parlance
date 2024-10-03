# parley.models
# Parley app models and database definition.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 17:59:43 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: models.py [] benjamin@rotational.io $

"""
Parley app models and database definition.
"""

##########################################################################
## Imports
##########################################################################

import uuid

from django.db import models
from .validators import validate_semver


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
        help_text="The globally unique identifier of the object"
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


##########################################################################
## LLM Models, Prompts, and Responses
##########################################################################

class LLM(BaseModel):
    """
    A record of an instantiated, trained LLM model to evaluate.
    """

    name = models.CharField(
        default=None, null=False, blank=False, max_length=255,
        help_text="The name of the model or model family being evaluated",
    )

    version = models.CharField(
        default="0.1.0", null=False, blank=False, max_length=32,
        help_text="The semantic version of the model for instance identification",
        validators=[validate_semver],
    )

    description = models.TextField(
        null=True, blank=True, default=None,
        help_text="Any notes or other descriptive information about the model or training process",
    )

    generation_config = models.JSONField(
        null=True, default=None, blank=True,
        help_text="The standardized generation config of the model",
    )

    quantization_info = models.JSONField(
        null=True, default=None, blank=True,
        help_text="Information about the quantization of the model, if any",
    )

    tokenizer_config = models.JSONField(
        null=True, default=None, blank=True,
        help_text="The standardized tokenization info of the model",
    )

    max_new_tokens = models.IntegerField(
        null=True, default=None, editable=True, blank=True,
        help_text="The maximum new tokens allowed during inferencing",
    )

    trained_on = models.DateTimeField(
        null=False, blank=False,
        help_text="The timestamp that the model started training"
    )

    training_duration = models.DurationField(
        null=True, default=None, blank=True,
        help_text="The amount of time it took to train the model"
    )

    class Meta:
        db_table = "llms"
        ordering = ("-trained_on",)
        get_latest_by = "trained_on"
        verbose_name = "LLM"
        verbose_name_plural = "LLMs"
        unique_together = ("name", "version")

    @property
    def training_completed(self):
        if self.trained_on is None or self.training_duration is None:
            return None
        return self.trained_on + self.training_duration


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
        null=False,
        blank=True,
        default="",
        help_text="Any notes or other descriptive information about the evaluation",
    )

    active = models.BooleanField(
        default=True,
        help_text="This prompt set should be used in evaluations of new models",
    )

    class Meta:
        db_table = "evaluations"
        ordering = ("-created",)
        get_latest_by = "created"
        verbose_name = "evaluation"
        verbose_name_plural = "evaluations"


class Prompt(BaseModel):
    """
    A prompt is a single instance of an input to an LLM.
    """

    system = models.TextField(
        null=True, default=None, blank=True,
        help_text="The system prompt specified to the LLM",
    )

    prompt = models.TextField(
        null=False, default=None, blank=False,
        help_text="The prompt used to generate an output from an LLM"
    )

    evaluation = models.ForeignKey(
        "parley.Evaluation",
        null=False,
        on_delete=models.CASCADE,
        related_name="prompts",
        help_text="The evaluation that this prompt is a part of"
    )

    history = models.JSONField(
        null=True, default=None, blank=True,
        help_text="An array of prompt IDs that precede this prompt during evaluation"
    )

    notes = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text="Any notes or other descriptive information about the prompt",
    )

    exclude = models.BooleanField(
        default=False,
        help_text="Exclude this prompt from evaluations and from metrics",
    )

    class Meta:
        db_table = "prompts"
        ordering = ("-created",)
        get_latest_by = "created"
        verbose_name = "prompt"
        verbose_name_plural = "prompts"


class Response(BaseModel):
    """
    A response is an output generated by an LLM to a specific prompt.
    """

    model = models.ForeignKey(
        "parley.LLM",
        null=False,
        on_delete=models.RESTRICT,
        related_name="responses",
        help_text="The LLM that generated the specified response",
    )

    prompt = models.ForeignKey(
        "parley.Prompt",
        null=False,
        on_delete=models.CASCADE,
        related_name="responses",
        help_text="The prompt that this is an LLM response to",
    )

    output = models.TextField(
        null=False,
        default=None,
        blank=False,
        help_text="The output generated by the LLM in response to the prompt",
    )

    max_new_tokens = models.IntegerField(
        null=True, default=None, editable=True, blank=True,
        help_text="Set this field if different from the model configuration",
    )

    inference_on = models.DateTimeField(
        null=False,
        blank=False,
        help_text="The timestamp that the LLM started the inferencing",
    )

    inference_duration = models.DurationField(
        null=True,
        default=None,
        blank=True,
        help_text="The amount of time it took to perform the inference",
    )

    class Meta:
        db_table = "responses"
        ordering = ("-created",)
        get_latest_by = "created"
        verbose_name = "response"
        verbose_name_plural = "responses"
