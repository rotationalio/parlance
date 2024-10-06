# Generated by Django 5.1.1 on 2024-10-06 19:35

import django.db.models.deletion
import parley.models.llm
import parley.validators
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Evaluation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The globally unique identifier of the object",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The timestamp that the object was created",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The timestamp that the object was last modified",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        default=None,
                        help_text="The descriptive name of the evaluation prompts collection",
                        max_length=255,
                    ),
                ),
                (
                    "task",
                    models.CharField(
                        default=None,
                        help_text="A description of the expected task or agent being evaluated",
                        max_length=255,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default=None,
                        help_text="Any notes or other descriptive information about the evaluation",
                        null=True,
                    ),
                ),
                (
                    "similarity_metric",
                    models.CharField(
                        choices=[
                            ("csti", "Cosine TF-IDF"),
                            ("cstf", "Cosine Term Frequency"),
                            ("jacc", "Jaccard"),
                            ("w2vc", "Cosine of Word2Vec Average"),
                            ("glve", "Cosine of GloVe Average"),
                            ("fast", "Cosine of FastText Average"),
                            ("d2vc", "Cosine of Doc2Vec"),
                            ("bert", "Cosine of BERT"),
                        ],
                        default="csti",
                        help_text="The similarity metric used to compare output to expected output",
                        max_length=4,
                    ),
                ),
                (
                    "similarity_threshold",
                    models.FloatField(
                        default=0.5,
                        help_text="The similarity threshold to determine if an output is generally correct or not",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text="This prompt set should be used in evaluations of new models",
                    ),
                ),
            ],
            options={
                "verbose_name": "evaluation",
                "verbose_name_plural": "evaluations",
                "db_table": "evaluations",
                "ordering": ("-created",),
                "get_latest_by": "created",
            },
        ),
        migrations.CreateModel(
            name="LLM",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The globally unique identifier of the object",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The timestamp that the object was created",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The timestamp that the object was last modified",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        default=None,
                        help_text="The name of the model or model family being evaluated",
                        max_length=255,
                    ),
                ),
                (
                    "version",
                    models.CharField(
                        default="0.1.0",
                        help_text="The semantic version of the model for instance identification",
                        max_length=32,
                        validators=[parley.validators.validate_semver],
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default=None,
                        help_text="Any notes or other descriptive information about the model or training process",
                        null=True,
                    ),
                ),
                (
                    "cover_image",
                    models.ImageField(
                        blank=True,
                        default=None,
                        help_text="A 4x3 image representing the model for the profile page",
                        null=True,
                        upload_to=parley.models.llm.llm_cover_upload_path,
                    ),
                ),
                (
                    "model_config",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="Configuration for instantiating the model",
                        null=True,
                    ),
                ),
                (
                    "generation_config",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="The standardized generation config of the model",
                        null=True,
                    ),
                ),
                (
                    "quantization_info",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="Information about the quantization of the model, if any",
                        null=True,
                    ),
                ),
                (
                    "tokenizer_config",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="The standardized tokenization info of the model",
                        null=True,
                    ),
                ),
                (
                    "max_new_tokens",
                    models.IntegerField(
                        blank=True,
                        default=None,
                        help_text="The maximum new tokens allowed during inferencing",
                        null=True,
                    ),
                ),
                (
                    "is_adapter_model",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Defines if this model is a base model or a LoRA",
                        null=True,
                    ),
                ),
                (
                    "trained_on",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        help_text="The timestamp that the model started training",
                        null=True,
                    ),
                ),
                (
                    "training_duration",
                    models.DurationField(
                        blank=True,
                        default=None,
                        help_text="The amount of time it took to train the model",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "LLM",
                "verbose_name_plural": "LLMs",
                "db_table": "llms",
                "ordering": ("-trained_on",),
                "get_latest_by": "trained_on",
            },
        ),
        migrations.CreateModel(
            name="Sensitive",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The timestamp that the object was created",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The timestamp that the object was last modified",
                    ),
                ),
                (
                    "term",
                    models.CharField(
                        help_text="The search term to look for sensitive data in output",
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    "is_regex",
                    models.BooleanField(
                        default=False,
                        help_text="If the term is a regular expression to analyze the output on",
                    ),
                ),
                (
                    "case_sensitive",
                    models.BooleanField(
                        default=False,
                        help_text="Do not use case insensitive search to locate the sensitive term",
                    ),
                ),
            ],
            options={
                "verbose_name": "sensitive",
                "verbose_name_plural": "sensitive",
                "db_table": "sensitive",
                "ordering": ("-created",),
                "get_latest_by": "created",
            },
        ),
        migrations.CreateModel(
            name="ModelEvaluation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The globally unique identifier of the object",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The timestamp that the object was created",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The timestamp that the object was last modified",
                    ),
                ),
                ("metrics_cached", models.BooleanField(default=False, editable=False)),
                (
                    "metrics_last_cached_on",
                    models.DateTimeField(default=None, editable=False, null=True),
                ),
                ("n_prompts", models.IntegerField(default=0, editable=False)),
                ("n_responses", models.IntegerField(default=0, editable=False)),
                (
                    "similarity_processed",
                    models.BooleanField(default=False, editable=False),
                ),
                ("n_similar", models.IntegerField(default=0, editable=False)),
                (
                    "labels_processed",
                    models.BooleanField(default=False, editable=False),
                ),
                ("n_labeled_correctly", models.IntegerField(default=0, editable=False)),
                (
                    "output_type_processed",
                    models.BooleanField(default=False, editable=False),
                ),
                ("n_valid_output_type", models.IntegerField(default=0, editable=False)),
                (
                    "sensitive_processed",
                    models.BooleanField(default=False, editable=False),
                ),
                ("n_leaks_sensitive", models.IntegerField(default=0, editable=False)),
                (
                    "confabulations_processed",
                    models.BooleanField(default=False, editable=False),
                ),
                ("n_confabulations", models.IntegerField(default=0, editable=False)),
                (
                    "readable_processed",
                    models.BooleanField(default=False, editable=False),
                ),
                ("n_readable", models.IntegerField(default=0, editable=False)),
                (
                    "evaluation",
                    models.ForeignKey(
                        help_text="The evaluation associated with the model",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="model_evaluations",
                        to="parley.evaluation",
                    ),
                ),
                (
                    "model",
                    models.ForeignKey(
                        help_text="The LLM that needs to be evaluated",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="model_evaluations",
                        to="parley.llm",
                    ),
                ),
            ],
            options={
                "db_table": "model_evaluations",
                "ordering": ("-created",),
                "get_latest_by": "created",
                "unique_together": {("model", "evaluation")},
            },
        ),
        migrations.AddField(
            model_name="llm",
            name="evaluations",
            field=models.ManyToManyField(
                through="parley.ModelEvaluation", to="parley.evaluation"
            ),
        ),
        migrations.AddField(
            model_name="evaluation",
            name="llms",
            field=models.ManyToManyField(
                through="parley.ModelEvaluation", to="parley.llm"
            ),
        ),
        migrations.CreateModel(
            name="Prompt",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The globally unique identifier of the object",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The timestamp that the object was created",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The timestamp that the object was last modified",
                    ),
                ),
                (
                    "system",
                    models.TextField(
                        blank=True,
                        default=None,
                        help_text="The system prompt specified to the LLM",
                        null=True,
                    ),
                ),
                (
                    "prompt",
                    models.TextField(
                        default=None,
                        help_text="The prompt used to generate an output from an LLM",
                    ),
                ),
                (
                    "history",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="An array of prompt IDs that precede this prompt during evaluation",
                        null=True,
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        default=None,
                        help_text="Any notes or other descriptive information about the prompt",
                        null=True,
                    ),
                ),
                (
                    "expected_output_type",
                    models.CharField(
                        choices=[
                            ("text", "text"),
                            ("json", "JSON"),
                            ("xml", "XML"),
                            ("csv", "CSV"),
                            ("img", "image"),
                            ("dviz", "Data Visualization"),
                        ],
                        default="text",
                        help_text="Specify the expected type of output for the prompt to validate",
                        max_length=4,
                    ),
                ),
                (
                    "expected_output",
                    models.TextField(
                        blank=True,
                        default=None,
                        help_text="Expected output for the prompt to use similarity scoring with",
                        null=True,
                    ),
                ),
                (
                    "expected_label",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text="For classifiers, expected label that should be contained in output",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "order",
                    models.IntegerField(
                        blank=True,
                        default=None,
                        help_text="Manually specify the order of the prompts for review",
                        null=True,
                    ),
                ),
                (
                    "exclude",
                    models.BooleanField(
                        default=False,
                        help_text="Exclude this prompt from evaluations and from metrics",
                    ),
                ),
                (
                    "evaluation",
                    models.ForeignKey(
                        help_text="The evaluation that this prompt is a part of",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prompts",
                        to="parley.evaluation",
                    ),
                ),
            ],
            options={
                "verbose_name": "prompt",
                "verbose_name_plural": "prompts",
                "db_table": "prompts",
                "ordering": ("evaluation__id", "order", "-created"),
                "get_latest_by": "created",
            },
        ),
        migrations.CreateModel(
            name="Response",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The globally unique identifier of the object",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The timestamp that the object was created",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The timestamp that the object was last modified",
                    ),
                ),
                (
                    "output",
                    models.TextField(
                        default=None,
                        help_text="The output generated by the LLM in response to the prompt",
                    ),
                ),
                (
                    "output_similarity",
                    models.FloatField(
                        blank=True,
                        default=None,
                        help_text="The similarity score of this response to the expected output",
                        null=True,
                    ),
                ),
                (
                    "is_similar",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Was the similarity score greater than the threshold?",
                        null=True,
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text="For classifiers, label that is extracted from the output",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "label_correct",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Was the output label correct based on the expected label (or almost correct for fuzzy label matching)",
                        null=True,
                    ),
                ),
                (
                    "valid_output_type",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text=(
                            "Based on the expected output type, is it parseable; e.g. if the output is supposed to be JSON, can it be correctly decoded?",
                        ),
                        null=True,
                    ),
                ),
                (
                    "leaks_sensitive",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Does the output contain sensitive data that should not be leaked?",
                        null=True,
                        verbose_name="leaks sensitive data",
                    ),
                ),
                (
                    "is_confabulation",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Is the output a hallucination or confabulation?",
                        null=True,
                    ),
                ),
                (
                    "is_readable",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Does the output contain grammatically correct, understandable language?",
                        null=True,
                    ),
                ),
                (
                    "max_new_tokens",
                    models.IntegerField(
                        blank=True,
                        default=None,
                        help_text="Set this field if different from the model configuration",
                        null=True,
                    ),
                ),
                (
                    "inference_on",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        help_text="The timestamp that the LLM started the inferencing",
                        null=True,
                    ),
                ),
                (
                    "inference_duration",
                    models.DurationField(
                        blank=True,
                        default=None,
                        help_text="The amount of time it took to perform the inference",
                        null=True,
                    ),
                ),
                (
                    "model",
                    models.ForeignKey(
                        help_text="The LLM that generated the specified response",
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="responses",
                        to="parley.llm",
                    ),
                ),
                (
                    "prompt",
                    models.ForeignKey(
                        help_text="The prompt that this is an LLM response to",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="responses",
                        to="parley.prompt",
                    ),
                ),
            ],
            options={
                "verbose_name": "response",
                "verbose_name_plural": "responses",
                "db_table": "responses",
                "ordering": ("-created",),
                "get_latest_by": "created",
            },
        ),
        migrations.CreateModel(
            name="ResponseReview",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The timestamp that the object was created",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The timestamp that the object was last modified",
                    ),
                ),
                (
                    "output_correct",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Was the output correct based on the expected output or the prompt (or almost correct for fuzzy qualitative correctness)?",
                        null=True,
                    ),
                ),
                (
                    "label_correct",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Was the output label correct based on the expected label (or almost correct for fuzzy label matching)?",
                        null=True,
                    ),
                ),
                (
                    "is_confabulation",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Is the output a hallucination or confabulation?",
                        null=True,
                    ),
                ),
                (
                    "is_readable",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text="Does the output contain grammatically correct, understandable language?",
                        null=True,
                    ),
                ),
                (
                    "response",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="parley.response",
                    ),
                ),
            ],
            options={
                "db_table": "response_reviews",
                "ordering": ("-created",),
                "get_latest_by": "created",
            },
        ),
        migrations.CreateModel(
            name="ReviewTask",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The timestamp that the object was created",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The timestamp that the object was last modified",
                    ),
                ),
                (
                    "started_on",
                    models.DateTimeField(
                        default=None,
                        help_text="The timestamp that the review was start on, null if not started",
                        null=True,
                    ),
                ),
                (
                    "completed_on",
                    models.DateTimeField(
                        default=None,
                        help_text="The timestamp that the review was completed, null if not completed",
                        null=True,
                    ),
                ),
                (
                    "evaluation",
                    models.ForeignKey(
                        help_text="The evaluation the user is performing",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review_tasks",
                        to="parley.evaluation",
                    ),
                ),
                (
                    "responses",
                    models.ManyToManyField(
                        through="parley.ResponseReview", to="parley.response"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="The user that is conducting the evaluation",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review_tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "review_tasks",
                "ordering": ("-created",),
                "get_latest_by": "created",
                "unique_together": {("user", "evaluation")},
            },
        ),
        migrations.AddField(
            model_name="responsereview",
            name="review",
            field=models.ForeignKey(
                help_text="The individual response reviews in a review",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="response_reviews",
                to="parley.reviewtask",
            ),
        ),
        migrations.AddField(
            model_name="response",
            name="reviewers",
            field=models.ManyToManyField(
                through="parley.ResponseReview", to="parley.reviewtask"
            ),
        ),
        migrations.AddField(
            model_name="evaluation",
            name="reviewers",
            field=models.ManyToManyField(
                through="parley.ReviewTask", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterUniqueTogether(
            name="llm",
            unique_together={("name", "version")},
        ),
        migrations.AlterUniqueTogether(
            name="responsereview",
            unique_together={("review", "response")},
        ),
        migrations.AlterUniqueTogether(
            name="response",
            unique_together={("model", "prompt")},
        ),
    ]
