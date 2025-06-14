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

import csv
import json

from collections import defaultdict

from django.views import View
from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.views.generic.edit import FormView
from django.views.generic import DetailView, ListView, UpdateView, DeleteView
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse, Http404, HttpResponseNotAllowed

from parley.exceptions import ParlanceUploadError
from parley.forms import (
    Uploader,
    CreateReviewForm,
    UpdateResponseReviewForm,
    EvaluationUploader,
)
from parley.models import LLM, Response, Evaluation, Prompt, ReviewTask, ResponseReview

BOOLEAN_METRICS = {
    "Similarity": ("similarity_processed", "n_is_similar", "n_not_similar"),
    "Correct Label": (
        "labels_processed",
        "n_labeled_correctly",
        "n_labeled_incorrectly",
    ),
    "Valid Output": (
        "valid_output_processed",
        "n_valid_output_type",
        "n_invalid_output_type",
    ),
    "Leaks Sensitive": (
        "sensitive_processed",
        "n_leaks_sensitive",
        "n_no_sensitive_leaks",
    ),
    "Is Readable": ("readability_processed", "n_readable", "n_not_readable"),
    "Is Factual": ("factual_processed", "n_factual", "n_not_factual"),
    "Is Correct Style": ("style_processed", "n_correct_style", "n_incorrect_style"),
}

CHART_METRICS = {
    "Similarity": (
        "similarity_processed",
        "percent_similar",
        "similarity_normalized",
    ),
    "Correct Label": ("labels_processed", "labels_percent", "labels_normalized"),
    "Valid Output": (
        "valid_output_processed",
        "percent_valid_output_type",
        "valid_output_normalized",
    ),
    "Leaks Sensitive": (
        "sensitive_processed",
        "percent_leaks_sensitive",
        "sensitive_normalized",
    ),
    "Is Readable": (
        "readability_processed",
        "percent_readable",
        "readability_normalized",
    ),
    "Is Factual": ("factual_processed", "percent_factual", "factual_normalized"),
    "Is Correct Style": (
        "style_processed",
        "percent_correct_style",
        "style_normalized",
    ),
    "Mean Helpfulness": (
        "helpfulness_processed",
        "mean_helpfulness",
        "mean_helpfulness_normalized",
    ),
    "Median Helpfulness": (
        "helpfulness_processed",
        "median_helpfulness",
        "median_helpfulness_normalized",
    ),
}


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


class EvaluationCreate(FormView):

    template_name = "evaluation/list.html"
    form_class = EvaluationUploader

    def get_success_url(self):
        # Redirect to the evaluation detail page after successful upload
        return reverse_lazy("evaluation-detail", kwargs={"pk": self.evaluation.pk})

    def form_valid(self, form):
        try:
            evaluation, counts = form.handle_upload()
        except ParlanceUploadError as e:
            # If an error occurs, stop processing and show the error to the user.
            form.add_error(None, str(e))
            return self.form_invalid(form)

        self.evaluation = evaluation
        messages.success(
            self.request,
            mark_safe(counts.html()),
        )
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])

    @transaction.atomic
    def post(self, *args, **kwargs):
        """
        Ensures that all database operations during a request are all or nothing.
        """
        return super().post(*args, **kwargs)


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

    def get_chart_data(self):
        # Colors
        # TODO: Use an actual color palette that we can dynamically select colors from
        colors = [
            "rgb(255, 99, 132)",
            "rgb(54, 162, 235)",
            "rgb(255, 206, 86)",
            "rgb(75, 192, 192)",
            "rgb(153, 102, 255)",
        ]
        color_index = 0

        models = self.object.model_evaluations.all()
        labels = [
            label
            for label, (has_metric, _, _) in CHART_METRICS.items()
            if getattr(models[0], has_metric)
        ]
        model_colors = {}
        for model in models:
            # Create a color for each model
            color = colors[color_index % len(colors)]
            color_index += 1
            model_colors[str(model.id)] = color

        # Create chart data
        datasets = []
        for model in models:
            dataset = {"label": model.model.name, "data": [], "trueValues": []}

            for metric_name, (
                processed,
                true_value,
                normalized,
            ) in CHART_METRICS.items():
                if metric_name not in labels:
                    continue

                if getattr(model, processed):
                    dataset["data"].append(getattr(model, normalized))
                    true_value = round(getattr(model, true_value), 2)
                    if metric_name in BOOLEAN_METRICS:
                        # Handle percentages
                        true_value = f"{true_value} %"
                    dataset["trueValues"].append(true_value)
                else:
                    dataset["data"].append(0)
                    dataset["trueValues"].append(0)

                dataset["borderColor"] = model_colors[str(model.id)]
                dataset["backgroundColor"] = model_colors[str(model.id)]

            datasets.append(dataset)

        # Ensure dataset values sum to 1 for each metric
        for i in range(len(labels)):
            # Get the values for this metric across all datasets
            total = sum(
                [
                    datasets[j]["data"][i]
                    for j in range(len(datasets))
                    if len(datasets[j]["data"]) > 0
                ]
            )
            if total > 0:
                for j in range(len(datasets)):
                    if len(datasets[j]["data"]) > 0:
                        datasets[j]["data"][i] /= total
                        datasets[j]["data"][i] = round(datasets[j]["data"][i], 2)

        return {"labels": labels, "datasets": datasets}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "evaluation"
        context["chart"] = self.get_chart_data()
        return context


class EvaluationDelete(DeleteView):
    """
    Delete an evaluation and all associated data.
    """

    model = Evaluation
    template_name = "evaluation/list.html"
    success_url = reverse_lazy("evaluations-list")

    def get(self, *args, **kwargs):
        """
        Prevent GET requests to delete an evaluation.
        """
        return HttpResponseNotAllowed(["POST"])


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
                "expected_label": prompt.expected_label,
            }

            reply.write(json.dumps(data) + "\n")

        return reply


class DownloadAnalytics(View):

    def get(self, request, pk=None):
        if pk is None or not Evaluation.objects.filter(pk=pk).exists():
            raise Http404("evaluation not found")

        evaluation = Evaluation.objects.get(pk=pk)
        filename = slugify(f"{evaluation.name}") + ".csv"

        reply = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

        fieldnames = ["id", "prompt", "expected"]
        models = [(llm.id, llm.name, llm.version) for llm in evaluation.llms.all()]
        for _, name, version in models:
            fieldnames.append(name + "-" + version)

        prompts = Prompt.objects.filter(evaluation__id=pk, exclude=False)
        writer = csv.DictWriter(reply, fieldnames=fieldnames)
        writer.writeheader()

        for prompt in prompts:
            values = [prompt.id, str(prompt), prompt.expected_label]
            for id, _, _ in models:
                response = Response.objects.filter(model__id=id, prompt=prompt).first()
                if response:
                    values.append(response.label)
                else:
                    values.append(None)

            writer.writerow(dict(zip(fieldnames, values)))

        return reply


##########################################################################
## LLM Views
##########################################################################


class LLMList(ListView):

    model = LLM
    template_name = "llm/list.html"
    context_object_name = "llms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "model"
        return context


class LLMDetail(DetailView):

    model = LLM
    template_name = "llm/detail.html"
    context_object_name = "llm"

    def get_chart_data(self):
        # Colors
        # TODO: Use an actual color palette that we can dynamically select colors from
        colors = [
            "rgb(255, 99, 132)",
            "rgb(54, 162, 235)",
            "rgb(255, 206, 86)",
            "rgb(75, 192, 192)",
            "rgb(153, 102, 255)",
        ]
        color_index = 0

        # Perform Aggregation
        chart = {"labels": [], "datasets": []}
        evaluations = {}
        normalized_values = defaultdict(lambda: defaultdict(float))
        for me in self.object.model_evaluations.all():
            for metric, (has_metric, value, normalized) in CHART_METRICS.items():
                if not getattr(me, has_metric):
                    continue

                # Get the normalized value
                normalized_value = getattr(me, normalized)
                normalized_values[metric][str(me.id)] = normalized_value
                evaluations[str(me.id)] = me.evaluation.name

        # Create the chart data
        for metric, values in normalized_values.items():
            chart["labels"].append(metric)
            for model, value in values.items():
                for ds in chart["datasets"]:
                    if ds["label"] == evaluations[model]:
                        break
                else:
                    color = colors[color_index % len(colors)]
                    color_index += 1
                    ds = {
                        "label": evaluations[model],
                        "data": [],
                        "borderColor": color,
                        "backgroundColor": color,
                    }
                    chart["datasets"].append(ds)
                ds["data"].append(value)

        return {key: json.dumps(val) for key, val in chart.items()}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "model"
        context["chart"] = self.get_chart_data()
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
        return HttpResponseNotAllowed(["POST"])


class ReviewTaskDetail(DetailView):

    model = ReviewTask
    template_name = "reviews/detail.html"
    context_object_name = "review"

    def get_response_object(self, **kwargs):
        # If the response is in the query string, fetch it.
        query = self.request.GET.get("response", None)
        if query:
            try:
                obj = Response.objects.get(pk=query)
                if (
                    obj.model != self.object.model
                    or obj.prompt.evaluation != self.object.evaluation
                ):
                    raise Http404
                return obj
            except Response.DoesNotExist:
                raise Http404

        # Otherwise get the latest response
        obj = Response.objects.filter(
            model=self.object.model,
            prompt__evaluation=self.object.evaluation,
        ).first()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "review"
        context["response"] = self.get_response_object()
        context["form"] = UpdateResponseReviewForm(
            instance=self.object.response_reviews.filter(
                review=context["review"], response=context["response"]
            ).first(),
        )
        context["form"].fields["response"].initial = context["response"]
        context["form"].fields["review"].initial = context["review"]
        return context


class UpdateResponseReview(UpdateView):
    """
    Update the review of a response.
    """

    model = ResponseReview
    form_class = UpdateResponseReviewForm
    success_url = reverse_lazy("dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["response"] = self.get_object().response
        context["review"] = self.get_object().review
        return context

    def get_success_url(self):
        review_id = self.request.POST.get("review")
        response_id = self.request.POST.get("response")
        url = reverse_lazy("review-task", kwargs={"pk": review_id})
        if response_id:
            url += f"?response={response_id}"
        return url

    def get_object(self):
        obj, _ = ResponseReview.objects.get_or_create(
            review_id=self.request.POST.get("review"),
            response_id=self.request.POST.get("response"),
        )
        return obj

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        raise SuspiciousOperation("unable to update review for logged in user")
