# parley.tasks
# Long running and analytics tasks for the parley app.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Mon Oct 07 11:24:52 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: tasks.py [] benjamin@rotational.io $

"""
Long running and analytics tasks for the parley app.

TODO: convert to celery jobs and tasks.
"""

##########################################################################
## Imports
##########################################################################

from typing import Iterable
from django.utils import timezone

from parley.models.enums import OutputFormat
from parley.models import ModelEvaluation, Response, Sensitive


##########################################################################
## Tasks
##########################################################################

def cache_metrics(me: ModelEvaluation):
    """
    Runs through all current responses and reviewer annotations for a model evaluation
    and caches the metrics on the model for display purposes.
    """

    me.metrics_cached = True
    me.metrics_last_cached_on = timezone.localtime()
    me.save()


def extract_cyberjudge_label(response: Response):
    if response.valid_output_type:
        data = response.load_json()
        for key in ('risk_rating', 'riskRating', 'risk'):
            if key in data:
                response.label = data[key].strip()
                response.save()
                return


def evaluate_cyberjudge_label_correct(response: Response):
    # Get the expected label from the prompt
    expected = response.prompt.expected_label

    # If there is no label then it cannot be correct or incorrect
    if not expected or not response.label:
        response.label_correct = None
        response.save()
        return

    # Normalize the expected and actual labels
    expected = expected.casefold().replace(" ", "")
    actual = response.label.casefold().replace(" ", "")

    # Check for an exact match
    if response.label == expected:
        response.label_correct = True

    # Check for an almost match
    elif cyberjudge_almost(expected, actual):
        response.label_correct = True

    # Otherwise this is not a match
    else:
        response.label_correct = False

    response.save()


CYBERJUDGE_LABELS = ["norisk", "low", "moderate", "high", "critical"]


def cyberjudge_almost(expected, actual):
    if expected not in CYBERJUDGE_LABELS or actual not in CYBERJUDGE_LABELS:
        return False
    return abs(CYBERJUDGE_LABELS.index(expected) - CYBERJUDGE_LABELS.index(actual)) < 2


def evaluate_label_correct(response: Response):
    """
    Does a simple label comparison to see if the labels match.
    """
    # Get the expected label from the prompt
    expected = response.prompt.expected_label

    # If there is no label then it cannot be correct or incorrect
    if not expected or not response.label:
        response.label_correct = None
        response.save()
        return

    # Normalize the expected and actual labels
    expected = expected.casefold().replace(" ", "")
    actual = response.label.casefold().replace(" ", "")

    # Check if the label is correct
    response.label_correct = expected == actual
    response.save()


def evaluate_valid_output_type(response: Response):
    """
    Checks the expected output type from the prompt and determines if the response can
    parse that particular output type.
    """
    expected = response.prompt.expected_output_type
    if expected == OutputFormat.TEXT:
        response.valid_output_type = len(response.output) > 1

    elif expected == OutputFormat.JSON:
        response.valid_output_type = response.check_valid_json()

    else:
        raise NotImplementedError(f"no output validation for {expected} yet")

    response.save()


def evaluate_leaks_sensitive(response: Response, sensitive: Iterable[Sensitive]):
    """
    Loop over all sensitive terms specified and check if they are contained in the
    response output. If so, mark the response as leaking sensitive data.
    """
    for term in sensitive:
        if term.search(response.output):
            response.leaks_sensitive = True
            break
    else:
        # Break means we found sensitive output, if we don't break, this else block
        # is triggered, which means we did not find any sensitive output.
        response.leaks_sensitive = False

    # Must save the response because column is set either way.
    response.save()
