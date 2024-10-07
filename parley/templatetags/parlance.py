# parley.templatetags.parlance
# Template tag helpers for parlance apps
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 21:52:22 2024 -0500
#
# ID: parlance.py [] benjamin@bengfort.com $

"""
Template tag helpers for parlance apps
"""

##########################################################################
## Imports
##########################################################################

from parlance import get_version
from parley.models import ReviewTask

from django import template
from django.contrib.messages import constants as messages

register = template.Library()


##########################################################################
## Template Tags
##########################################################################


@register.simple_tag()
def version():
    return get_version(short=True, revision=False)


@register.filter(name="alert_level")
def alert_level(level):
    return {
        messages.INFO: "alert-info",
        messages.SUCCESS: "alert-success",
        messages.WARNING: "alert-warning",
        messages.ERROR: "alert-danger",
    }.get(level, "alert-dark")


@register.simple_tag()
def get_review_task(user, evaluation):
    try:
        return ReviewTask.objects.get(user=user, model_evaluation=evaluation)
    except ReviewTask.DoesNotExist:
        return None
