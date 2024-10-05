# parley.admin
# Parley app administrative configuration.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 17:59:43 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: admin.py [] benjamin@rotational.io $

"""
Parley app administrative configuration.
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin

from .models import Sensitive
from .models import Evaluation, Prompt
from .models import ReviewTask, ResponseReview
from .models import LLM, ModelEvaluation, Response


# Register your models here.
admin.site.register(Sensitive)
admin.site.register(Evaluation)
admin.site.register(Prompt)
admin.site.register(ReviewTask)
admin.site.register(ResponseReview)
admin.site.register(LLM)
admin.site.register(ModelEvaluation)
admin.site.register(Response)
