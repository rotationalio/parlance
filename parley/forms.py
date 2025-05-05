# parley.forms
# Forms for handling and validating user input.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Wed Oct 02 14:04:48 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: forms.py [] benjamin@rotational.io $

"""
Forms for handling and validating user input.
"""

##########################################################################
## Imports
##########################################################################

import os
import json
import tempfile
from datetime import datetime, timedelta

from django import forms
from collections import defaultdict
from django.utils.timezone import make_aware
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from parley.exceptions import ParlanceUploadError
from django.core.exceptions import ValidationError
from parley.models import ModelEvaluation, ReviewTask, ResponseReview
from parley.models import LLM, Evaluation, Prompt, Response, Sensitive


##########################################################################
## Fields
##########################################################################


class MultipleFileInput(forms.ClearableFileInput):

    allow_multiple_selected = True


class MultipleFileField(forms.FileField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


##########################################################################
## Helpers
##########################################################################


class UploaderCounts(object):

    def __init__(self):
        # Stores files: objects: operation: count
        self.counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    def increment(self, fname, obj, created):
        if created:
            self.created(fname, obj.__class__.__name__)
        else:
            self.updated(fname, obj.__class__.__name__)

    def created(self, fname, otype):
        self.counts[fname][otype]["created"] += 1

    def updated(self, fname, otype):
        self.counts[fname][otype]["updated"] += 1

    def html(self):
        lines = [
            f'<h4 class="alert-heading">Upload Complete: {len(self.counts)} File(s) Processed</h4>'
        ]

        row = 0
        for fname, ocounts in self.counts.items():
            # Make sure every file has an hr accept the last one.
            if row != 0:
                lines.append("<hr />")
            row += 1

            lines.append(
                f'<p class="mb-1"><code>{fname}</code> results:</p>\n<ul class="my-0">'
            )
            for otype, c in ocounts.items():
                lines.append(
                    f'<li><code>{otype}</code>: {c["created"]} created, {c["updated"]} updated'
                )
            lines.append("</ul>")

        return "\n".join(lines)


##########################################################################
## Forms
##########################################################################


class BaseUploader(forms.Form):

    def read_jsonlines(self, path):
        with open(path, "r") as f:
            for i, line in enumerate(f.readlines()):
                try:
                    yield i + 1, json.loads(line)
                except json.JSONDecodeError:
                    fname = os.path.basename(path)
                    raise ParlanceUploadError(f"invalid json on line {i+1} of {fname}")

    def write_temporary_file(self, td, f):
        path = os.path.join(td, f.name)
        with open(path, "wb") as fh:
            for chunk in f.chunks():
                fh.write(chunk)
        return path


class Uploader(BaseUploader):

    jsonl = MultipleFileField(allow_empty_file=False)

    def clean_jsonl(self):
        files = self.cleaned_data["jsonl"]
        for f in files:
            # Ensure these files are JSON lines files
            _, ext = os.path.splitext(f.name)
            if ext not in {".jsonl", ".jsonlines"}:
                raise ValidationError("must specify only .jsonlines or .jsonl files")
        return files

    def handle_upload(self):
        counts = UploaderCounts()
        files = self.cleaned_data["jsonl"]
        with tempfile.TemporaryDirectory() as td:
            for f in files:
                self.handle_uploaded_file(td, f, counts)
        return counts

    def handle_uploaded_file(self, td, f, counts):
        # Write the file to a temporary file on disk
        path = self.write_temporary_file(td, f)

        # Read the temporary file and handle contents
        for r, row in self.read_jsonlines(path):
            if "type" not in row:
                raise ParlanceUploadError(f"missing type field on line {r} of {f.name}")

            rtype = {
                "llm": LLM,
                "evaluation": Evaluation,
                "prompt": Prompt,
                "response": Response,
                "sensitive": Sensitive,
            }.get(row.pop("type").strip().lower(), None)

            if rtype is None:
                raise ParlanceUploadError(
                    f"unknown type \"{row['type']}\" on line {r} of {f.name}"
                )

            # Handle Foreign Keys
            if rtype == Prompt:
                self.link_reference(row, "evaluation", Evaluation)
            elif rtype == Response:
                self.link_reference(row, "model", LLM)
                self.link_reference(row, "prompt", Prompt)

            counts.increment(f.name, *rtype.objects.get_or_create(**row))

    def link_reference(self, row, key, model):
        try:
            row[key] = model.objects.get(id=row[key])
        except (KeyError, model.DoesNotExist):
            raise ParlanceUploadError(
                f"could not associate \"{row.get(key, '')}\" with existing {model.__name__} object"
            )


class EvaluationUploader(BaseUploader):

    name = forms.CharField(required=True)
    task = forms.CharField(required=True)
    description = forms.CharField(required=False)
    models_file = forms.FileField(required=True)
    prompts_file = forms.FileField(allow_empty_file=False)

    def parse_message(self, message, allowed_roles=["system", "user", "assistant"]):
        # Ensure the message has a role and content
        role = message.get("role", None)
        if role not in allowed_roles:
            raise ValidationError(f"expected 'role' field to be one of {allowed_roles}")
        content = message.get("content", None)
        if content is None:
            raise ValidationError("missing 'content' field in message")
        return role, content

    def parse_chat_messages(self, messages):
        # Must be at least one message
        if not isinstance(messages, list):
            raise ValidationError("expected 'messages' field to be a list")
        if len(messages) < 1:
            raise ValidationError("expected at least one message in 'messages' field")

        # System message is the first message if present
        role, content = self.parse_message(
            messages[0], allowed_roles=["system", "user"]
        )
        if role == "system":
            system = content
            if len(messages) < 2:
                raise ValidationError(
                    "expected at least one user message in 'messages' field"
                )
            role, content = self.parse_message(messages[1], allowed_roles=["user"])
            user = content
        else:
            system = None
            user = content
        return system, user

    def parse_chat_completions(self, completions):
        # Must be at least one completion
        if not isinstance(completions, list):
            raise ValidationError("expected 'completions' field to be a list")
        if len(completions) < 1:
            raise ValidationError(
                "expected at least one completion in 'completions' field"
            )

        # Assume first completion is the best
        _, content = self.parse_message(completions[0], allowed_roles=["assistant"])
        return content

    def parse_prompt(self, obj):
        messages = obj.get("messages", None)
        if messages is not None:
            system, prompt = self.parse_chat_messages(messages)
            completions = obj.get("completions", None)
            if completions is None:
                raise ValidationError("expected 'completions' field in prompt")
            response = self.parse_chat_completions(completions)
        else:
            system = obj.get("system", None)
            prompt = obj.get("prompt", None)
            response = obj.get("response", None)
            if prompt is None:
                raise ValidationError("expected 'prompt' field in prompt")
            if response is None:
                raise ValidationError("expected 'response' field in prompt")
        model = obj.get("model", None)
        if model is None:
            raise ValidationError("expected 'model' field in prompt")
        return system, prompt, response, model

    def parse_model(self, obj):
        # Ensure the model JSON has a name and created field
        name = obj.get("name", None)
        if name is None:
            raise ValidationError("expected 'name' field in model JSON")
        created = obj.get("created", None)
        if created is None:
            raise ValidationError("expected 'created' field in model JSON")
        try:
            created = make_aware(datetime.fromtimestamp(created))
        except Exception:
            raise ValidationError(
                f'could not parse created field "{created}", expected a unix timestamp'
            )
        return name, created

    def handle_upload(self):
        # Create the evaluation object
        evaluation = Evaluation.objects.create(
            name=self.cleaned_data["name"],
            task=self.cleaned_data["task"],
            description=self.cleaned_data.get("description", ""),
        )

        counts = UploaderCounts()
        with tempfile.TemporaryDirectory() as td:
            # Process the models file and create the LLMs
            model_file = self.cleaned_data["models_file"]
            path = self.write_temporary_file(td, model_file)
            for r, row in self.read_jsonlines(path):
                try:
                    name, created = self.parse_model(row)
                except ValidationError as e:
                    raise ParlanceUploadError(
                        f"invalid model JSON on line {r} of {model_file.name}: {e}"
                    )
                llm, _ = LLM.objects.get_or_create(name=name, trained_on=created)
                evaluation.llms.add(llm)
                counts.increment(model_file.name, llm, True)

            # Process the prompts file
            order = 1
            prompts = set()
            prompts_file = self.cleaned_data["prompts_file"]
            path = self.write_temporary_file(td, prompts_file)
            for r, row in self.read_jsonlines(path):
                try:
                    system, user, assistant, model = self.parse_prompt(row)
                except ValidationError as e:
                    raise ParlanceUploadError(
                        f"invalid prompt JSON on line {r} of {prompts_file.name}: {e}"
                    )
                key = (system, user)
                if key not in prompts:
                    prompt = Prompt.objects.create(
                        system=system,
                        prompt=user,
                        order=order,
                        evaluation=evaluation,
                    )
                    prompts.add(key)
                    order += 1
                    counts.increment(prompts_file.name, prompt, True)
                else:
                    prompt = Prompt.objects.get(
                        system=system,
                        prompt=user,
                        evaluation=evaluation,
                    )

                # Add the response for this prompt
                try:
                    llm = LLM.objects.get(name=model, evaluation=evaluation)
                except LLM.DoesNotExist:
                    raise ParlanceUploadError(f"could not find model by name '{model}'")

                # We only support one response per prompt per model
                try:
                    response = Response.objects.create(
                        model=llm,
                        prompt=prompt,
                        output=assistant,
                        inference_on=(
                            make_aware(datetime.fromtimestamp(row["inference_on"]))
                            if "inference_on" in row
                            else None
                        ),
                        inference_duration=(
                            timedelta(seconds=row["inference_seconds"])
                            if "inference_seconds" in row
                            else None
                        ),
                    )
                except IntegrityError:
                    raise ParlanceUploadError(
                        f"duplicate prompt for model '{model}' at line {r} of {prompts_file.name}"
                    )
                counts.increment(prompts_file.name, response, True)

        return evaluation, counts


class CreateReviewForm(forms.Form):

    user = forms.IntegerField(required=True)
    evaluation = forms.UUIDField(required=True)

    def save(self):
        try:
            ReviewTask.objects.create(
                user=User.objects.get(pk=self.cleaned_data["user"]),
                model_evaluation=ModelEvaluation.objects.get(
                    pk=self.cleaned_data["evaluation"]
                ),
            )
        except (User.DoesNotExist, ModelEvaluation.DoesNotExist):
            return


class UpdateResponseReviewForm(forms.ModelForm):
    class Meta:
        model = ResponseReview
        fields = [
            "is_readable",
            "is_factual",
            "is_correct_style",
            "helpfulness",
            "review",
            "response",
        ]

    def is_complete(self):
        if not hasattr(self, "cleaned_data"):
            if self.is_bound:
                self.is_valid()
            else:
                if self.instance and self.instance.pk:
                    return (
                        self.instance.is_readable is not None
                        and self.instance.is_factual is not None
                        and self.instance.is_correct_style is not None
                        and self.instance.helpfulness is not None
                    )
                return False

        check_fields = ["is_readable", "is_factual", "is_correct_style", "helpfulness"]
        return all(self.cleaned_data.get(field) is not None for field in check_fields)

    def save(self):
        response_review, _ = ResponseReview.objects.get_or_create(
            review=self.cleaned_data["review"],
            response=self.cleaned_data["response"],
        )

        for key, value in self.cleaned_data.items():
            if key not in ["review", "response"]:
                setattr(response_review, key, value)

        response_review.save()
        return response_review
