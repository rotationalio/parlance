# parley.signals
# Signals used by the parley app to maintain database correctness.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Sat Oct 05 17:25:10 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: signals.py [] benjamin@rotational.io $

"""
Signals used by the parley app to maintain database correctness.
"""

##########################################################################
## Imports
##########################################################################

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from parley.models import Response, ModelEvaluation


##########################################################################
## Ensure Models are Linked to Evaluations
##########################################################################

@receiver(post_save, sender=Response, dispatch_uid="model_evaluation_linkage")
def model_evaluation_linkage(sender, instance, created, *args, **kwargs):
    """
    If a response has been created and the model is not associated with the
    evaluation the prompt of the response is associated with, then create a
    model evaluation object to track it.
    """
    if created:
        kwargs = {
            "model": instance.model,
            "evaluation": instance.prompt.evaluation
        }

        if not ModelEvaluation.objects.filter(**kwargs).exists():
            ModelEvaluation.objects.create(**kwargs)


@receiver(post_delete, sender=Response, dispatch_uid="model_evaluation_unlink")
def model_evaluation_unlink(sender, instance, *args, **kwargs):
    """
    If a response has been deleted and the model is no longer associated with any
    prompts in the evaluation, unlink the model and the evaluation from the db.
    """
    kwargs = {
        "model": instance.model,
        "prompt__evaluation": instance.prompt.evaluation
    }

    if Response.objects.filter(**kwargs).count() == 0:
        try:
            kwargs["evaluation"] = kwargs.pop("prompt__evaluation")
            ModelEvaluation.objects.get(**kwargs).delete()
        except ModelEvaluation.DoesNotExist:
            pass
