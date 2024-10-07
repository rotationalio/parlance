# parley.views
# Parley views and controllers.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 17:59:43 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: views.py [] benjamin@rotational.io $

"""
Parley views and controllers.
"""

##########################################################################
## Imports
##########################################################################

import json

from django.views import View
from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic.edit import FormView
from django.views.generic import DetailView, ListView
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse, Http404, HttpResponseNotAllowed

from parley.exceptions import ParlanceUploadError
from parley.forms import Uploader, CreateReviewForm
from parley.models import LLM, Response, Evaluation, Prompt


##########################################################################
## Views
##########################################################################

class UploaderFormView(FormView):

    template_name = "site/upload.html"
    form_class = Uploader
    success_url = reverse_lazy("upload")

    def form_valid(self, form):
        # Handle the uploaded data stored in the form
        try:
            counts = form.handle_upload()
        except ParlanceUploadError as e:
            # If an error occurs, stop processing and show the error to the user.
            form.add_error(None, str(e))
            return self.form_invalid(form)

        # Create the success message with the counts
        messages.success(self.request, mark_safe(counts.html()))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "upload"
        return context

    @transaction.atomic
    def post(self, *args, **kwargs):
        """
        Ensures that all database operations during a request are all or nothing.
        """
        return super().post(*args, **kwargs)


##########################################################################
## Evaluation Views
##########################################################################

class EvaluationList(ListView):

    model = Evaluation
    template_name = "evaluation/list.html"
    context_object_name = "evaluations"

    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "evaluation"
        return context


class EvaluationDetail(DetailView):

    model = Evaluation
    template_name = "evaluation/detail.html"
    context_object_name = "evaluation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "evaluation"
        return context


class DownloadPrompts(View):

    def get(self, request, pk=None):
        if pk is None or not Evaluation.objects.filter(pk=pk).exists():
            raise Http404("evaluation not found")

        prompts = Prompt.objects.filter(evaluation__id=pk, exclude=False)

        reply = HttpResponse(
            content_type="application/jsonlines",
            headers={"Content-Disposition": 'attachment; filename="prompts.jsonl"'},
        )

        for prompt in prompts:
            data = {
                "id": str(prompt.id),
                "evaluation": str(pk),
                "system": prompt.system,
                "prompt": prompt.prompt,
                "history": prompt.history,
                "notes": prompt.notes,
                "expected_output_type": prompt.expected_output_type,
                "expected_output": prompt.expected_output,
                "expected_labe": prompt.expected_label
            }

            reply.write(json.dumps(data) + "\n")
        return reply


##########################################################################
## LLM Views
##########################################################################


class LLMList(ListView):

    model = LLM
    template_name = "llm/list.html"
    context_object_name = "llm"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "model"
        return context


class LLMDetail(DetailView):

    model = LLM
    template_name = "llm/detail.html"
    context_object_name = "llm"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "model"
        return context


##########################################################################
## Response Views
##########################################################################

class ResponseDetail(DetailView):

    model = Response
    template_name = "response/detail.html"
    context_object_name = "response"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "response"
        return context


##########################################################################
## Review Tasks
##########################################################################

class CreateReviewTask(FormView):

    form_class = CreateReviewForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        raise SuspiciousOperation("unable to create review task for logged in user")

    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])
