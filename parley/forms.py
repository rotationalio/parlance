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

from django import forms
from collections import defaultdict
from django.contrib.auth.models import User
from parley.exceptions import ParlanceUploadError
from django.core.exceptions import ValidationError
from parley.models import ModelEvaluation, ReviewTask
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
        self.counts[fname][otype]['updated'] += 1

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

            lines.append(f'<p class="mb-1"><code>{fname}</code> results:</p>\n<ul class="my-0">')
            for otype, c in ocounts.items():
                lines.append(f'<li><code>{otype}</code>: {c["created"]} created, {c["updated"]} updated')
            lines.append('</ul>')

        return "\n".join(lines)


##########################################################################
## Forms
##########################################################################

class Uploader(forms.Form):

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
            if 'type' not in row:
                raise ParlanceUploadError(
                    f"missing type field on line {r} of {f.name}"
                )

            rtype = {
                'llm': LLM,
                'evaluation': Evaluation,
                'prompt': Prompt,
                'response': Response,
                'sensitive': Sensitive,
            }.get(row.pop('type').strip().lower(), None)

            if rtype is None:
                raise ParlanceUploadError(
                    f"unknown type \"{row['type']}\" on line {r} of {f.name}"
                )

            # Handle Foreign Keys
            if rtype == Prompt:
                self.link_reference(row, 'evaluation', Evaluation)
            elif rtype == Response:
                self.link_reference(row, 'model', LLM)
                self.link_reference(row, 'prompt', Prompt)

            counts.increment(f.name, *rtype.objects.get_or_create(**row))

    def read_jsonlines(self, path):
        with open(path, 'r') as f:
            for i, line in enumerate(f.readlines()):
                try:
                    yield i+1, json.loads(line)
                except json.JSONDecodeError:
                    fname = os.path.basename(path)
                    raise ParlanceUploadError(f"invalid json on line {i+1} of {fname}")

    def write_temporary_file(self, td, f):
        path = os.path.join(td, f.name)
        with open(path, 'wb') as fh:
            for chunk in f.chunks():
                fh.write(chunk)
        return path

    def link_reference(self, row, key, model):
        try:
            row[key] = model.objects.get(id=row[key])
        except (KeyError, model.DoesNotExist):
            raise ParlanceUploadError(
                f"could not associate \"{row.get(key, '')}\" with existing {model.__name__} object"
            )


class CreateReviewForm(forms.Form):

    user = forms.IntegerField(required=True)
    evaluation = forms.UUIDField(required=True)

    def save(self):
        try:
            ReviewTask.objects.create(
                user=User.objects.get(
                    pk=self.cleaned_data["user"]
                ),
                model_evaluation=ModelEvaluation.objects.get(
                    pk=self.cleaned_data["evaluation"]
                ),
            )
        except (User.DoesNotExist, ModelEvaluation.DoesNotExist):
            return
