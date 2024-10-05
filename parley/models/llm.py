# parley.models.llm
# LLM models for evaluation and their responses.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Sat Oct 05 15:11:26 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: llm.py [] benjamin@rotational.io $

"""
LLM models for evaluation and their responses.
"""

##########################################################################
## Imports
##########################################################################

import os
import json

from .base import BaseModel
from django.db import models
from django.urls import reverse

from parley.validators import validate_semver


##########################################################################
## Helpers
##########################################################################

def llm_cover_upload_path(instance, filename):
    _, ext = os.path.splitext(filename)
    return os.path.join("covers", "llms", f"{instance.id}{ext}")


##########################################################################
## Models
##########################################################################

class LLM(BaseModel):
    """
    A record of an instantiated, trained LLM model to evaluate.
    """

    name = models.CharField(
        default=None,
        null=False,
        blank=False,
        max_length=255,
        help_text="The name of the model or model family being evaluated",
    )

    version = models.CharField(
        default="0.1.0",
        null=False,
        blank=False,
        max_length=32,
        help_text="The semantic version of the model for instance identification",
        validators=[validate_semver],
    )

    description = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text="Any notes or other descriptive information about the model or training process",
    )

    cover_image = models.ImageField(
        null=True,
        blank=True,
        default=None,
        upload_to=llm_cover_upload_path,
        help_text="A 4x3 image representing the model for the profile page",
    )

    model_config = models.JSONField(
        null=True,
        default=None,
        blank=True,
        help_text="Configuration for instantiating the model",
    )

    generation_config = models.JSONField(
        null=True,
        default=None,
        blank=True,
        help_text="The standardized generation config of the model",
    )

    quantization_info = models.JSONField(
        null=True,
        default=None,
        blank=True,
        help_text="Information about the quantization of the model, if any",
    )

    tokenizer_config = models.JSONField(
        null=True,
        default=None,
        blank=True,
        help_text="The standardized tokenization info of the model",
    )

    max_new_tokens = models.IntegerField(
        null=True,
        default=None,
        editable=True,
        blank=True,
        help_text="The maximum new tokens allowed during inferencing",
    )

    is_adapter_model = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text="Defines if this model is a base model or a LoRA",
    )

    trained_on = models.DateTimeField(
        null=True,
        default=None,
        blank=True,
        help_text="The timestamp that the model started training",
    )

    training_duration = models.DurationField(
        null=True,
        default=None,
        blank=True,
        help_text="The amount of time it took to train the model",
    )

    evaluations = models.ManyToManyField(
        'parley.Evaluation', through='parley.ModelEvaluation',
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

    def __str__(self):
        return self.name


class ModelEvaluation(BaseModel):
    """
    Models must be linked to specific evaluations in order to understand the
    performance of the model for the evaluation. Note that models are also linked to
    evaluations via their responses, but this model makes it easier to track aggregate
    data. This table represents a denormalization since the foreign keys are duplicated,
    but it makes application semantics a lot simpler.

    This table ensures there is a many to many relationship between models and
    evaluations.
    """

    model = models.ForeignKey(
        "parley.LLM",
        null=False,
        on_delete=models.CASCADE,
        related_name="model_evaluations",
        help_text="The LLM that needs to be evaluated",
    )

    evaluation = models.ForeignKey(
        "parley.Evaluation",
        null=False,
        on_delete=models.CASCADE,
        related_name="model_evaluations",
        help_text="The evaluation associated with the model",
    )

    # Cache Info
    metrics_cached = models.BooleanField(
        default=False, editable=False,
    )

    # Cache Info
    metrics_last_cached_on = models.DateTimeField(
        default=None, null=True, editable=False,
    )

    # Cached metric
    n_prompts = models.IntegerField(
        default=0, editable=False,
    )

    # Cached metric
    n_responses = models.IntegerField(
        default=0, editable=False,
    )

    # Processing Info
    similarity_processed = models.BooleanField(
        default=False, editable=False,
    )

    # Cached metric
    n_similar = models.IntegerField(
        default=0, editable=False,
    )

    # Processing Info
    labels_processed = models.BooleanField(
        default=False, editable=False,
    )

    # Cached metric
    n_labeled_correctly = models.IntegerField(
        default=0, editable=False,
    )

    # Processing Info
    output_type_processed = models.BooleanField(
        default=False, editable=False,
    )

    # Cached metric
    n_valid_output_type = models.IntegerField(
        default=0, editable=False,
    )

    # Processing Info
    sensitive_processed = models.BooleanField(
        default=False, editable=False,
    )

    # Cached metric
    n_leaks_sensitive = models.IntegerField(
        default=0, editable=False,
    )

    # Processing Info
    confabulations_processed = models.BooleanField(
        default=False, editable=False,
    )

    # Cached metric
    n_confabulations = models.IntegerField(
        default=0, editable=False,
    )

    # Processing Info
    readable_processed = models.BooleanField(
        default=False, editable=False,
    )

    # Cached metric
    n_readable = models.IntegerField(
        default=0, editable=False,
    )

    class Meta:
        db_table = "model_evaluations"
        ordering = ("-created",)
        get_latest_by = "created"
        unique_together = ('model', 'evaluation')

    @property
    def image(self):
        return self.model.image

    def responses(self):
        return Response.objects.filter(
            model=self.model, prompt__evaluation=self.evaluation
        )

    def __str__(self):
        return f"{self.evaluation.name} for {self.model.name}"


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

    output_similarity = models.FloatField(
        null=True,
        default=None,
        blank=True,
        help_text="The similarity score of this response to the expected output",
    )

    is_similar = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text="Was the similarity score greater than the threshold?",
    )

    label = models.CharField(
        null=True,
        blank=True,
        default=None,
        max_length=255,
        help_text="For classifiers, label that is extracted from the output",
    )

    label_correct = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text=(
            "Was the output label correct based on the expected label "
            "(or almost correct for fuzzy label matching)"
        ),
    )

    # For text - check to make sure it contains expected characters.
    valid_output_type = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text=(
            "Based on the expected output type, is it parseable; e.g. if the "
            "output is supposed to be JSON, can it be correctly decoded?",
        ),
    )

    leaks_sensitive = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        verbose_name="leaks sensitive data",
        help_text="Does the output contain sensitive data that should not be leaked?",
    )

    # TODO: set this based on annotator agreement
    is_confabulation = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text="Is the output a hallucination or confabulation?",
    )

    # TODO: set this based on annotator agreement
    is_readable = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text="Does the output contain grammatically correct, understandable language?",
    )

    max_new_tokens = models.IntegerField(
        null=True,
        default=None,
        editable=True,
        blank=True,
        help_text="Set this field if different from the model configuration",
    )

    inference_on = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text="The timestamp that the LLM started the inferencing",
    )

    inference_duration = models.DurationField(
        null=True,
        default=None,
        blank=True,
        help_text="The amount of time it took to perform the inference",
    )

    reviewers = models.ManyToManyField(
        "parley.ReviewTask", through="parley.ResponseReview"
    )

    class Meta:
        db_table = "responses"
        ordering = ("-created",)
        get_latest_by = "created"
        verbose_name = "response"
        verbose_name_plural = "responses"
        unique_together = ("model", "prompt")

    @property
    def evaluation(self):
        return self.prompt.evaluation

    def get_previous(self):
        try:
            return self.get_previous_by_created()
        except self.DoesNotExist:
            return None

    def get_next(self):
        try:
            return self.get_next_by_created()
        except self.DoesNotExist:
            return None

    def get_absolute_url(self):
        return reverse("response-detail", args=(self.id,))

    def validate_json(self):
        output = self.output.strip()
        output = output.removeprefix("```json").removesuffix("```").strip()
        try:
            json.loads(output)
            return True
        except json.JSONDecodeError:
            return False
